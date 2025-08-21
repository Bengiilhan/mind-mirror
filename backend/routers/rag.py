"""
RAG Router - Kişiselleştirilmiş Terapi Teknikleri API
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel

from models import User
from auth import get_current_user
from agents.rag_agent import RAGAgent

router = APIRouter()

# Pydantic modelleri
class TechniqueRequest(BaseModel):
    distortion_type: str
    user_context: Optional[str] = None

class MultipleTechniquesRequest(BaseModel):
    distortion_types: List[str]
    user_context: Optional[str] = None

# RAG agent instance
rag_agent = RAGAgent()

@router.post("/techniques/")
async def get_therapy_techniques(
    request: TechniqueRequest,
    current_user: User = Depends(get_current_user)
):
    """Belirli bir çarpıtma türü için terapi teknikleri önerir"""
    try:
        techniques = await rag_agent.get_therapy_techniques(
            distortion_type=request.distortion_type,
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

@router.post("/techniques/multiple/")
async def get_multiple_techniques(
    request: MultipleTechniquesRequest,
    current_user: User = Depends(get_current_user)
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
