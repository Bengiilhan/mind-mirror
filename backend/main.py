from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import json
from dotenv import load_dotenv
from typing import Optional
from datetime import datetime

from database import engine, get_db
from models import Base, User, Entry, Analysis
from schemas import UserCreate, UserLogin, UserResponse, Token, EntryCreate, EntryUpdate, EntryResponse
from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from agents.analyze import router as analyze_router
from typing import List

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zihin Aynası API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "Authorization", "Content-Type"],
    expose_headers=["*"],
)

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Entry endpoints (protected)
@app.post("/entries/", response_model=EntryResponse)
def create_entry(entry: EntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_entry = Entry(
        text=entry.text,
        mood_score=entry.mood_score,
        user_id=current_user.id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Eğer analiz sonucu gönderilmişse onu kullan, yoksa yeni analiz yap
    analysis_data = None
    
    # Frontend'den gelen analiz sonucunu kontrol et
    if hasattr(entry, 'analysis') and entry.analysis:
        analysis_data = entry.analysis
        print("✅ Frontend'den gelen analiz sonucu kullanılıyor")
    else:
        # Yeni analiz yap
        try:
            from agents.cognitive_agent import CognitiveAnalysisAgent
            cognitive_agent = CognitiveAnalysisAgent()
            import asyncio
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                analysis_result = loop.run_until_complete(
                    cognitive_agent.analyze_entry(
                        text=entry.text,
                        user_id=str(current_user.id)
                    )
                )
                analysis_data = analysis_result
                print(f"✅ Yeni analiz yapıldı: {len(analysis_result.get('distortions', []))} çarpıtma")
            finally:
                loop.close()
        except Exception as e:
            print(f"❌ Analiz hatası: {e}")
            analysis_data = {
                "distortions": [],
                "overall_mood": "belirsiz",
                "error": "Analiz yapılamadı",
                "analysis_timestamp": datetime.now().isoformat()
            }

    # Analysis tablosuna kaydet
    if analysis_data:
        db_analysis = Analysis(
            entry_id=db_entry.id,
            result=analysis_data
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)

    entry_dict = {
        "id": db_entry.id,
        "text": db_entry.text,
        "mood_score": db_entry.mood_score,
        "created_at": db_entry.created_at,
        "user_id": db_entry.user_id,
        "analysis": analysis_data
    }

    return EntryResponse(**entry_dict)

@app.get("/entries/", response_model=List[EntryResponse])
def get_entries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries = (
        db.query(Entry)
        .filter(Entry.user_id == current_user.id)
        .order_by(Entry.created_at.desc())
        .all()
    )

    result = []
    for entry in entries:
        analysis_obj = entry.analysis

        if analysis_obj and analysis_obj.result:
            raw = analysis_obj.result
            if isinstance(raw, str):
                try:
                    parsed_analysis = json.loads(raw)
                except json.JSONDecodeError:
                    parsed_analysis = None
            elif isinstance(raw, dict):
                parsed_analysis = raw
            else:
                parsed_analysis = None
        else:
            parsed_analysis = None

        entry_dict = {
            "id": entry.id,
            "text": entry.text,
            "mood_score": entry.mood_score,
            "created_at": entry.created_at,
            "user_id": entry.user_id,
            "analysis": parsed_analysis  # DİKKAT: Burada dict olmalı!
        }

        result.append(EntryResponse(**entry_dict))
    
    return result



@app.put("/entries/{entry_id}", response_model=EntryResponse)
def update_entry(entry_id: int, entry_update: EntryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry_update.text is not None:
        db_entry.text = entry_update.text
    if entry_update.mood_score is not None:
        db_entry.mood_score = entry_update.mood_score
    
    db.commit()
    db.refresh(db_entry)
    
    # EntryResponse formatında döndür
    analysis_data = None
    if hasattr(db_entry, 'analysis') and db_entry.analysis and db_entry.analysis.result:
        raw = db_entry.analysis.result
        if isinstance(raw, str):
            try:
                analysis_data = json.loads(raw)
            except json.JSONDecodeError:
                analysis_data = None
        elif isinstance(raw, dict):
            analysis_data = raw

    entry_dict = {
        "id": db_entry.id,
        "text": db_entry.text,
        "mood_score": db_entry.mood_score,
        "created_at": db_entry.created_at,
        "user_id": db_entry.user_id,
        "analysis": analysis_data
    }

    return EntryResponse(**entry_dict)

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # İlişkili analiz kaydı varsa önce onu sil
    try:
        analysis_obj = db.query(Analysis).filter(Analysis.entry_id == db_entry.id).first()
        if analysis_obj:
            db.delete(analysis_obj)
            db.flush()
    except Exception:
        # Analiz silme denemesi başarısız olsa bile giriş silme işlemini engelleme
        pass

    db.delete(db_entry)
    db.commit()
    return {"message": "Entry deleted successfully"}

# Health check
@app.get("/")
def read_root():
    return {"message": "Zihin Aynası API is running"}
    
app.include_router(analyze_router, prefix="/analyze", tags=["AI Analysis"])

# İstatistik router'ını ekle
from routers.statistics import router as statistics_router
app.include_router(statistics_router, tags=["Statistics"])

# RAG router'ını ekle
from routers.rag import router as rag_router
app.include_router(rag_router, prefix="/rag", tags=["RAG - Terapi Teknikleri"])
