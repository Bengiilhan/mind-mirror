"""
Report Agent - Haftalık ve aylık analiz raporları üretir
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

@dataclass
class WeeklyStats:
    """Haftalık istatistikler"""
    total_entries: int
    total_distortions: int
    most_common_distortion: str
    mood_trend: str
    improvement_areas: List[str]
    recommendations: List[str]

class WeeklyReport(BaseModel):
    """Haftalık rapor modeli"""
    week_start: str
    week_end: str
    total_entries: int
    total_distortions: int
    distortion_breakdown: Dict[str, int]
    mood_summary: str
    key_insights: List[str]
    recommendations: List[str]
    progress_score: float
    generated_at: str

class ReportAgent:
    """Haftalık ve aylık rapor üretimi için agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.output_parser = JsonOutputParser(pydantic_object=WeeklyReport)
        
        # Rapor üretim prompt'u
        self.report_prompt = ChatPromptTemplate.from_messages([
            ("system", """Sen bir psikoloji uzmanısın. Kullanıcının haftalık günlük verilerini 
            analiz ederek detaylı bir rapor hazırlamakla görevlisin.
            
            Rapor şunları içermeli:
            1. Genel istatistikler (toplam yazı, çarpıtma sayısı)
            2. Çarpıtma türlerinin dağılımı
            3. Ruh hali trendi
            4. Ana içgörüler
            5. Kişiselleştirilmiş öneriler
            6. İlerleme puanı (0-100)
            
            Sadece JSON formatında yanıt ver."""),
            ("human", """Aşağıdaki haftalık verileri analiz et ve rapor hazırla:
            
            Hafta: {week_start} - {week_end}
            Toplam yazı: {total_entries}
            Çarpıtma verileri: {distortion_data}
            Ruh hali verileri: {mood_data}
            
            Detaylı rapor hazırla.""")
        ])
    
    async def generate_weekly_report(
        self, 
        user_id: str, 
        week_start: datetime,
        entries_data: List[Dict[str, Any]]
    ) -> WeeklyReport:
        """Haftalık rapor üretir"""
        try:
            week_end = week_start + timedelta(days=6)
            
            # Verileri analiz et
            stats = self._analyze_weekly_data(entries_data)
            
            # LLM ile rapor üret
            report_data = await self._generate_report_with_llm(
                week_start=week_start.strftime("%Y-%m-%d"),
                week_end=week_end.strftime("%Y-%m-%d"),
                total_entries=stats.total_entries,
                distortion_data=stats.distortions,
                mood_data=stats.mood_trend
            )
            
            return WeeklyReport(**report_data)
            
        except Exception as e:
            # Hata durumunda basit rapor üret
            return self._generate_fallback_report(week_start, entries_data, str(e))
    
    def _analyze_weekly_data(self, entries_data: List[Dict[str, Any]]) -> WeeklyStats:
        """Haftalık verileri analiz eder"""
        total_entries = len(entries_data)
        total_distortions = 0
        distortion_counts = {}
        mood_scores = []
        
        for entry in entries_data:
            # Çarpıtma sayısını hesapla
            distortions = entry.get("distortions", [])
            total_distortions += len(distortions)
            
            # Çarpıtma türlerini say
            for distortion in distortions:
                dist_type = distortion.get("type", "bilinmeyen")
                distortion_counts[dist_type] = distortion_counts.get(dist_type, 0) + 1
            
            # Ruh hali puanını al
            mood_score = entry.get("mood_score", 5)  # Varsayılan 5
            mood_scores.append(mood_score)
        
        # En yaygın çarpıtmayı bul
        most_common = max(distortion_counts.items(), key=lambda x: x[1])[0] if distortion_counts else "yok"
        
        # Ruh hali trendini hesapla
        if mood_scores:
            avg_mood = sum(mood_scores) / len(mood_scores)
            if avg_mood > 6:
                mood_trend = "iyileşme"
            elif avg_mood < 4:
                mood_trend = "kötüleşme"
            else:
                mood_trend = "stabil"
        else:
            mood_trend = "belirsiz"
        
        # İyileştirme alanlarını belirle
        improvement_areas = []
        if distortion_counts.get("felaketleştirme", 0) > 2:
            improvement_areas.append("Gelecek kaygıları")
        if distortion_counts.get("genelleme", 0) > 2:
            improvement_areas.append("Genelleme yapma eğilimi")
        if distortion_counts.get("kişiselleştirme", 0) > 2:
            improvement_areas.append("Kişiselleştirme")
        
        # Öneriler üret
        recommendations = []
        if total_distortions > 10:
            recommendations.append("Bu hafta çok sayıda çarpıtma tespit edildi. Daha fazla mindfulness pratiği yapmayı deneyin.")
        if mood_trend == "kötüleşme":
            recommendations.append("Ruh halinizde düşüş var. Profesyonel destek almayı düşünebilirsiniz.")
        
        return WeeklyStats(
            total_entries=total_entries,
            total_distortions=total_distortions,
            most_common_distortion=most_common,
            mood_trend=mood_trend,
            improvement_areas=improvement_areas,
            recommendations=recommendations
        )
    
    async def _generate_report_with_llm(
        self,
        week_start: str,
        week_end: str,
        total_entries: int,
        distortion_data: Dict[str, int],
        mood_data: str
    ) -> Dict[str, Any]:
        """LLM ile detaylı rapor üretir"""
        try:
            chain = (
                self.report_prompt
                | self.llm
                | self.output_parser
            )
            
            result = await chain.ainvoke({
                "week_start": week_start,
                "week_end": week_end,
                "total_entries": total_entries,
                "distortion_data": json.dumps(distortion_data, ensure_ascii=False),
                "mood_data": mood_data
            })
            
            return result
            
        except Exception as e:
            # LLM hatası durumunda basit rapor üret
            return self._generate_simple_report(week_start, week_end, total_entries, distortion_data, mood_data)
    
    def _generate_simple_report(
        self,
        week_start: str,
        week_end: str,
        total_entries: int,
        distortion_data: Dict[str, int],
        mood_data: str
    ) -> Dict[str, Any]:
        """Basit rapor üretir (LLM hatası durumunda)"""
        total_distortions = sum(distortion_data.values())
        
        # İlerleme puanını hesapla
        if total_entries == 0:
            progress_score = 0
        else:
            # Çarpıtma oranına göre puan hesapla
            distortion_ratio = total_distortions / total_entries
            if distortion_ratio < 0.5:
                progress_score = 80 + (1 - distortion_ratio) * 20
            elif distortion_ratio < 1.0:
                progress_score = 60 + (1 - distortion_ratio) * 20
            else:
                progress_score = max(20, 60 - (distortion_ratio - 1) * 20)
        
        return {
            "week_start": week_start,
            "week_end": week_end,
            "total_entries": total_entries,
            "total_distortions": total_distortions,
            "distortion_breakdown": distortion_data,
            "mood_summary": f"Ruh hali trendi: {mood_data}",
            "key_insights": [
                f"Bu hafta {total_entries} günlük yazısı yazıldı",
                f"Toplam {total_distortions} bilişsel çarpıtma tespit edildi",
                f"En yaygın çarpıtma: {max(distortion_data.items(), key=lambda x: x[1])[0] if distortion_data else 'yok'}"
            ],
            "recommendations": [
                "Düzenli günlük tutmaya devam edin",
                "Tespit edilen çarpıtmalar üzerinde çalışın",
                "Alternatif düşünceleri pratik edin"
            ],
            "progress_score": round(progress_score, 1),
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_fallback_report(
        self,
        week_start: datetime,
        entries_data: List[Dict[str, Any]],
        error_message: str
    ) -> WeeklyReport:
        """Hata durumunda fallback rapor üretir"""
        week_end = week_start + timedelta(days=6)
        
        return WeeklyReport(
            week_start=week_start.strftime("%Y-%m-%d"),
            week_end=week_end.strftime("%Y-%m-%d"),
            total_entries=len(entries_data),
            total_distortions=0,
            distortion_breakdown={},
            mood_summary="Veri analizi sırasında hata oluştu",
            key_insights=[f"Hata: {error_message}"],
            recommendations=["Lütfen daha sonra tekrar deneyin"],
            progress_score=0.0,
            generated_at=datetime.now().isoformat()
        )
    
    async def generate_monthly_summary(
        self,
        user_id: str,
        month: int,
        year: int,
        weekly_reports: List[WeeklyReport]
    ) -> Dict[str, Any]:
        """Aylık özet rapor üretir"""
        try:
            total_entries = sum(report.total_entries for report in weekly_reports)
            total_distortions = sum(report.total_distortions for report in weekly_reports)
            
            # Çarpıtma türlerini birleştir
            monthly_distortions = {}
            for report in weekly_reports:
                for dist_type, count in report.distortion_breakdown.items():
                    monthly_distortions[dist_type] = monthly_distortions.get(dist_type, 0) + count
            
            # İlerleme trendini hesapla
            progress_trend = "iyileşme" if len(weekly_reports) >= 2 and \
                weekly_reports[-1].progress_score > weekly_reports[0].progress_score else "stabil"
            
            return {
                "month": month,
                "year": year,
                "total_entries": total_entries,
                "total_distortions": total_distortions,
                "monthly_distortions": monthly_distortions,
                "progress_trend": progress_trend,
                "weekly_progress": [report.progress_score for report in weekly_reports],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Aylık özet üretilirken hata: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }