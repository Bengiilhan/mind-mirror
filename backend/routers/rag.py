"""
RAG Router - Kişiselleştirilmiş Terapi Teknikleri API
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
from models import User
from auth import get_current_user
from agents.rag_agent import RAGAgent

router = APIRouter()

# Pydantic modelleri
class TechniqueRequest(BaseModel):
    distortion_type: str
    user_context: Optional[str] = None
    save_to_entry: Optional[bool] = False

class MultipleTechniquesRequest(BaseModel):
    distortion_types: List[str]
    user_context: Optional[str] = None

# RAG agent instance
rag_agent = RAGAgent()

@router.post("/techniques/")
async def get_therapy_techniques(
    request: TechniqueRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir çarpıtma türü için terapi teknikleri önerir"""
    try:
        techniques = await rag_agent.get_therapy_techniques(
            distortion_type=request.distortion_type,
            user_context=request.user_context
        )
        
        # Eğer kaydetme isteniyorsa, kullanıcının son entry'sine RAG tekniklerini ekle
        if request.save_to_entry:
            from models import Entry
            from sqlalchemy import desc
            
            # Kullanıcının en son entry'sini bul
            latest_entry = db.query(Entry).filter(
                Entry.user_id == current_user.id
            ).order_by(desc(Entry.created_at)).first()
            
            if latest_entry:
                # Entry'nin analysis alanını güncelle
                if latest_entry.analysis:
                    if isinstance(latest_entry.analysis, str):
                        import json
                        analysis_data = json.loads(latest_entry.analysis)
                    else:
                        analysis_data = latest_entry.analysis
                else:
                    analysis_data = {}
                
                # RAG tekniklerini analysis'a ekle
                if 'rag_techniques' not in analysis_data:
                    analysis_data['rag_techniques'] = {}
                
                analysis_data['rag_techniques'][request.distortion_type] = techniques
                
                # Entry'yi güncelle
                latest_entry.analysis = analysis_data
                db.commit()
        
        return {
            "success": True,
            "data": techniques,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Teknikler alınırken hata oluştu: {str(e)}"
        )

@router.post("/techniques/multiple/")
async def get_multiple_techniques(
    request: MultipleTechniquesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Birden fazla çarpıtma türü için teknikler önerir"""
    try:
        techniques = await rag_agent.get_multiple_techniques(
            distortion_types=request.distortion_types,
            user_context=request.user_context
        )
        
        return {
            "success": True,
            "data": techniques,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Teknikler alınırken hata oluştu: {str(e)}"
        )

@router.get("/distortions/")
async def get_available_distortions(
    current_user: User = Depends(get_current_user)
):
    """Mevcut çarpıtma türlerini döndürür"""
    try:
        distortions = rag_agent.get_available_distortions()
        summary = rag_agent.get_technique_summary()
        
        return {
            "success": True,
            "data": {
                "distortions": distortions,
                "summary": summary,
                "total_techniques": sum(summary.values())
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Çarpıtma türleri alınırken hata oluştu: {str(e)}"
        )

@router.get("/health/")
async def rag_health_check():
    """RAG sisteminin sağlık durumunu kontrol eder"""
    try:
        distortions = rag_agent.get_available_distortions()
        summary = rag_agent.get_technique_summary()
        
        return {
            "status": "healthy",
            "available_distortions": len(distortions),
            "total_techniques": sum(summary.values()),
            "agent_type": "RAG Agent - Terapi Teknikleri"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent_type": "RAG Agent - Terapi Teknikleri"
        }
