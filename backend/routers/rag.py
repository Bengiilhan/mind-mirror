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
    enable_personalization: bool = True

class MultipleTechniquesRequest(BaseModel):
    distortion_types: List[str]
    user_context: Optional[str] = None
    enable_personalization: bool = True

class SimilarEntriesRequest(BaseModel):
    query_text: str
    distortion_type: Optional[str] = None
    n_results: int = 5

# RAG agent instance
rag_agent = RAGAgent()

@router.post("/techniques/")
async def get_therapy_techniques(
    request: TechniqueRequest,
    current_user: User = Depends(get_current_user)
):
    """Belirli bir çarpıtma türü için terapi teknikleri önerir (ChromaDB destekli)"""
    try:
        # Kişiselleştirme için user_id ekle
        user_id = str(current_user.id) if request.enable_personalization else None
        
        techniques = await rag_agent.get_therapy_techniques(
            distortion_type=request.distortion_type,
            user_context=request.user_context,
            user_id=user_id
        )
        
        return {
            "success": True,
            "data": techniques,
            "user_id": current_user.id,
            "personalization_enabled": request.enable_personalization,
            "source": techniques.get("source", "unknown")
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
        # Kişiselleştirme için user_id ekle
        user_id = str(current_user.id) if request.enable_personalization else None
        
        techniques = await rag_agent.get_multiple_techniques(
            distortion_types=request.distortion_types,
            user_context=request.user_context,
            user_id=user_id
        )
        
        return {
            "success": True,
            "data": techniques,
            "user_id": current_user.id,
            "personalization_enabled": request.enable_personalization
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
        
        # ChromaDB durumu
        chroma_status = "enabled" if rag_agent.use_chroma else "disabled"
        
        return {
            "status": "healthy",
            "available_distortions": len(distortions),
            "total_techniques": sum(summary.values()),
            "chromadb_status": chroma_status,
            "agent_type": "RAG Agent - Terapi Teknikleri (ChromaDB Enhanced)"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "chromadb_status": "unknown",
            "agent_type": "RAG Agent - Terapi Teknikleri"
        }

# -----------------------------------------------------------------------------
# ChromaDB Destekli Yeni Endpoint'ler
# -----------------------------------------------------------------------------

@router.post("/similar-entries/")
async def find_similar_entries(
    request: SimilarEntriesRequest,
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının benzer geçmiş deneyimlerini bulur"""
    try:
        if not rag_agent.use_chroma:
            return {
                "success": False,
                "message": "ChromaDB mevcut değil",
                "data": []
            }
        
        similar_entries = await rag_agent.chroma_service.find_similar_entries(
            user_id=str(current_user.id),
            query_text=request.query_text,
            distortion_type=request.distortion_type,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "data": {
                "similar_entries": similar_entries,
                "query": request.query_text,
                "total_found": len(similar_entries),
                "distortion_filter": request.distortion_type
            },
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benzer girişler aranırken hata oluştu: {str(e)}"
        )

@router.get("/user-insights/")
async def get_user_insights(
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının düşünce kalıpları ve istatistikleri"""
    try:
        insights = await rag_agent.get_user_insights(str(current_user.id))
        
        return {
            "success": True,
            "data": insights,
            "user_id": current_user.id,
            "generated_at": insights.get("analysis_period", {}).get("last_analysis", "")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Kullanıcı içgörüleri alınırken hata oluştu: {str(e)}"
        )

@router.get("/chroma-stats/")
async def get_chroma_statistics(
    current_user: User = Depends(get_current_user)
):
    """ChromaDB istatistiklerini döndürür"""
    try:
        if not rag_agent.use_chroma:
            return {
                "success": False,
                "message": "ChromaDB mevcut değil",
                "data": {}
            }
        
        stats = await rag_agent.chroma_service.get_collection_stats()
        
        return {
            "success": True,
            "data": stats,
            "chromadb_enabled": True,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ChromaDB istatistikleri alınırken hata oluştu: {str(e)}"
        )

@router.post("/techniques/semantic-search/")
async def semantic_technique_search(
    request: SimilarEntriesRequest,
    current_user: User = Depends(get_current_user)
):
    """Semantik arama ile ilgili teknikleri bulur"""
    try:
        if not rag_agent.use_chroma:
            return {
                "success": False,
                "message": "ChromaDB mevcut değil",
                "data": []
            }
        
        # Çarpıtma türü filtresini liste haline getir
        distortion_filter = [request.distortion_type] if request.distortion_type else None
        
        techniques = await rag_agent.chroma_service.find_relevant_techniques(
            query_text=request.query_text,
            distortion_types=distortion_filter,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "data": {
                "techniques": techniques,
                "query": request.query_text,
                "total_found": len(techniques),
                "distortion_filter": request.distortion_type
            },
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantik teknik arama hatası: {str(e)}"
        )
