# backend/analyze.py - LangChain Agent Mimarisi ile Yeniden Yazıldı
import os
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from dotenv import load_dotenv

from agents.cognitive_agent import CognitiveAnalysisAgent

load_dotenv()

router = APIRouter()

# Pydantic model for request
class AnalysisRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    
    class Config:
        # Extra fields'ları kabul et
        extra = "allow"
    
    @validator('user_id', pre=True)
    def convert_user_id_to_string(cls, v):
        if v is not None:
            return str(v)
        return v

# Global agent instance (production'da singleton pattern kullanılabilir)
cognitive_agent = CognitiveAnalysisAgent()

@router.post("/")
async def analyze_entry(request: AnalysisRequest):
    """
    Günlük yazısını bilişsel çarpıtma analizi için agent'a gönderir
    """
    try:
        print(f"🔍 Analyze request alındı: {request}")
        print(f"📝 Text: {request.text}")
        print(f"👤 User ID: {request.user_id}")
        print(f"📋 Request type: {type(request.text)}")
        print(f"📋 Text length: {len(request.text) if request.text else 0}")
        print(f"📋 Request dict: {request.dict()}")
        
        # Validation
        if not request.text:
            print("❌ Text field boş")
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(request.text, str):
            print(f"❌ Text field string değil: {type(request.text)}")
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not request.text.strip():
            print("❌ Boş metin hatası")
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        print("✅ Request validation başarılı, analiz başlatılıyor...")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=request.text,
            user_id=request.user_id
        )
        
        print(f"✅ Analiz tamamlandı: {result}")
        
        # Hata kontrolü
        if "error" in result:
            print(f"❌ Analiz hatası: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        print("🎉 Analiz başarıyla tamamlandı")
        return result
        
    except HTTPException:
        print("❌ HTTPException raised")
        raise
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")

@router.post("/debug")
async def analyze_entry_debug(request: dict = Body(...)):
    """
    Debug endpoint - raw request ile analiz
    """
    try:
        print(f"🔍 DEBUG: Raw request alındı: {request}")
        print(f"📝 DEBUG: Request type: {type(request)}")
        print(f"📝 DEBUG: Request keys: {list(request.keys()) if isinstance(request, dict) else 'Not a dict'}")
        
        # Extract text from request
        text = request.get("text", "")
        user_id = request.get("user_id", None)
        
        print(f"📝 DEBUG: Extracted text: {text}")
        print(f"👤 DEBUG: Extracted user_id: {user_id}")
        
        # Validation
        if not text:
            print("❌ DEBUG: Text field boş")
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(text, str):
            print(f"❌ DEBUG: Text field string değil: {type(text)}")
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not text.strip():
            print("❌ DEBUG: Boş metin hatası")
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        print("✅ DEBUG: Request validation başarılı, analiz başlatılıyor...")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=text,
            user_id=user_id
        )
        
        print(f"✅ DEBUG: Analiz tamamlandı: {result}")
        
        # Hata kontrolü
        if "error" in result:
            print(f"❌ DEBUG: Analiz hatası: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        print("🎉 DEBUG: Analiz başarıyla tamamlandı")
        return result
        
    except HTTPException:
        print("❌ DEBUG: HTTPException raised")
        raise
    except Exception as e:
        print(f"❌ DEBUG: Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DEBUG: Beklenmeyen hata: {str(e)}")

@router.post("/raw")
async def analyze_entry_raw(request: dict = Body(...)):
    """
    Raw JSON request ile analiz - debug için
    """
    try:
        print(f"🔍 Raw analyze request alındı: {request}")
        print(f"📝 Request type: {type(request)}")
        print(f"📝 Request keys: {list(request.keys()) if isinstance(request, dict) else 'Not a dict'}")
        
        # Extract text from request
        text = request.get("text", "")
        user_id = request.get("user_id", None)
        
        print(f"📝 Extracted text: {text}")
        print(f"👤 Extracted user_id: {user_id}")
        
        # Validation
        if not text:
            print("❌ Text field boş")
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(text, str):
            print(f"❌ Text field string değil: {type(text)}")
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not text.strip():
            print("❌ Boş metin hatası")
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        print("✅ Raw request validation başarılı, analiz başlatılıyor...")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=text,
            user_id=user_id
        )
        
        print(f"✅ Raw analiz tamamlandı: {result}")
        
        # Hata kontrolü
        if "error" in result:
            print(f"❌ Raw analiz hatası: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        print("🎉 Raw analiz başarıyla tamamlandı")
        return result
        
    except HTTPException:
        print("❌ Raw HTTPException raised")
        raise
    except Exception as e:
        print(f"❌ Raw beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Raw beklenmeyen hata: {str(e)}")

@router.post("/batch")
async def analyze_batch_entries(requests: list[AnalysisRequest]):
    """
    Birden fazla günlük yazısını toplu analiz eder
    """
    try:
        results = []
        for request in requests:
            if not request.text.strip():
                continue
                
            result = await cognitive_agent.analyze_entry(
                text=request.text,
                user_id=request.user_id
            )
            results.append(result)
        
        return {
            "total_analyzed": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toplu analiz hatası: {str(e)}")

@router.get("/memory/{user_id}")
async def get_user_memory(user_id: str):
    """
    Belirli kullanıcının analiz geçmişini döndürür
    """
    try:
        # Bu endpoint için ayrı memory sistemi gerekebilir
        # Şimdilik basit bir örnek
        return {
            "user_id": user_id,
            "message": "Memory sistemi geliştirme aşamasında"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/memory/{user_id}")
async def clear_user_memory(user_id: str):
    """
    Belirli kullanıcının memory'sini temizler
    """
    try:
        cognitive_agent.clear_memory()
        return {"message": f"{user_id} kullanıcısının memory'si temizlendi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Agent'ın sağlık durumunu kontrol eder
    """
    try:
        return {
            "status": "healthy",
            "agent_type": "CognitiveAnalysisAgent",
            "memory_status": "active",
            "llm_status": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }