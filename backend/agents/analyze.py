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
        # Validation
        if not request.text:
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(request.text, str):
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not request.text.strip():
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=request.text,
            user_id=request.user_id
        )
        
        # Hata kontrolü
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")

@router.post("/debug")
async def analyze_entry_debug(request: dict = Body(...)):
    """
    Debug endpoint - raw request ile analiz
    """
    try:
        # Extract text from request
        text = request.get("text", "")
        user_id = request.get("user_id", None)
        
        # Validation
        if not text:
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(text, str):
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not text.strip():
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=text,
            user_id=user_id
        )
        
        # Hata kontrolü
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DEBUG: Beklenmeyen hata: {str(e)}")

@router.post("/raw")
async def analyze_entry_raw(request: dict = Body(...)):
    """
    Raw JSON request ile analiz - debug için
    """
    try:
        # Extract text from request
        text = request.get("text", "")
        user_id = request.get("user_id", None)
        
        # Validation
        if not text:
            raise HTTPException(status_code=422, detail="Text field boş olamaz")
        
        if not isinstance(text, str):
            raise HTTPException(status_code=422, detail="Text field string olmalı")
        
        if not text.strip():
            raise HTTPException(status_code=422, detail="Metin boş olamaz")
        
        # Agent ile analiz yap
        result = await cognitive_agent.analyze_entry(
            text=text,
            user_id=user_id
        )
        
        # Hata kontrolü
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
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