"""
İstatistik Router - Kullanıcı ilerleme takibi
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
from auth import get_current_user
from models import User
from services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Kullanıcının istatistiklerini döndürür"""
    try:
        stats_service = StatisticsService()
        stats = stats_service.get_user_statistics(db, current_user.id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İstatistik hatası: {str(e)}")

@router.get("/insights")
async def get_ai_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """AI ile üretilen içgörüleri döndürür"""
    try:
        from models import Entry
        
        # Kullanıcının son girişlerini al
        entries = db.query(Entry).filter(Entry.user_id == current_user.id).order_by(Entry.created_at.desc()).limit(10).all()
        
        if not entries:
            raise HTTPException(status_code=404, detail="Henüz giriş bulunamadı")
        
        # İstatistikleri hesapla
        stats_service = StatisticsService()
        stats = stats_service.get_user_statistics(db, current_user.id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        # AI içgörüleri üret
        entry_texts = [entry.text for entry in entries if entry.text]
        ai_insights = await stats_service.generate_ai_insights(entry_texts, stats)
        
        return {
            "ai_insights": ai_insights,
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İçgörü hatası: {str(e)}")

@router.get("/progress")
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """İlerleme özetini döndürür"""
    try:
        stats_service = StatisticsService()
        stats = stats_service.get_user_statistics(db, current_user.id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        # İlerleme özeti
        progress = {
            "total_entries": stats.get("entry_count", 0),
            "total_distortions": stats.get("total_distortions", 0),
            "avg_distortions_per_entry": round(stats.get("total_distortions", 0) / stats.get("entry_count", 1), 2),
            "dominant_mood": stats.get("mood_analysis", {}).get("dominant_mood", "belirsiz"),
            "high_risk_percentage": stats.get("risk_analysis", {}).get("high_risk_percentage", 0),
            "most_common_distortion": stats.get("distortion_stats", {}).get("most_common", [{}])[0].get("type", "yok") if stats.get("distortion_stats", {}).get("most_common") else "yok"
        }
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İlerleme hatası: {str(e)}")
