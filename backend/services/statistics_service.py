"""
İstatistik Servisi - Kullanıcı ilerleme analizi
Bu servis, kullanıcının günlük girişlerini analiz ederek istatistiksel raporlar üretir.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models import Entry, Analysis, User
from agents.cognitive_agent import CognitiveAnalysisAgent

class StatisticsService:
    """Kullanıcı istatistikleri için servis"""
    
    def __init__(self):
        self.cognitive_agent = CognitiveAnalysisAgent()
    
    def should_generate_stats(self, entry_count: int) -> bool:
        """İstatistik oluşturulup oluşturulmayacağını belirler"""
        # İlk 5 girişte istatistik oluştur
        if entry_count == 5:
            return True
        
        # Sonrasında her 10 girişte bir güncelle
        if entry_count > 5 and entry_count % 10 == 0:
            return True
        
        return False
    
    def get_next_milestone(self, entry_count: int) -> int:
        """Bir sonraki milestone'u döndürür"""
        if entry_count < 5:
            return 5
        else:
            return ((entry_count // 10) + 1) * 10
    
    def get_user_statistics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Kullanıcının istatistiklerini hesaplar"""
        try:
            # Kullanıcının tüm girişlerini al
            entries = db.query(Entry).filter(Entry.user_id == user_id).order_by(Entry.created_at).all()
            
            if not entries:
                return {
                    "entry_count": 0,
                    "analyzed_entries": 0,
                    "total_distortions": 0,
                    "distortion_stats": {
                        "total": 0,
                        "most_common": [],
                        "severity_distribution": {},
                        "average_confidence": 0
                    },
                    "mood_analysis": {
                        "total_entries": 0,
                        "mood_distribution": {},
                        "recent_trend": [],
                        "dominant_mood": "belirsiz",
                        "mood_timeline": [],
                        "trend_direction": "belirsiz",
                        "trend_percentage": 0
                    },
                    "risk_analysis": {
                        "total_entries": 0,
                        "high_risk_entries": 0,
                        "medium_risk_entries": 0,
                        "low_risk_entries": 0,
                        "high_risk_percentage": 0,
                        "medium_plus_risk_percentage": 0,
                        "risk_distribution": {},
                        "trend": "belirsiz"
                    },
                    "progress_insights": {
                        "summary": "Henüz günlük girişi yapmadın. İlk girişini yaptıktan sonra istatistiklerin burada görünecek.",
                        "recommendations": [],
                        "progress_indicators": {}
                    },
                    "exercise_recommendations": {
                        "daily_exercises": [],
                        "weekly_challenges": [],
                        "emergency_tools": [],
                        "focus_areas": []
                    },
                    "last_updated": datetime.now().isoformat()
                }
            
            # Analiz verilerini topla
            all_distortions = []
            mood_scores = []
            risk_levels = []
            entry_texts = []
            
            for entry in entries:
                if entry.analysis and entry.analysis.result:
                    analysis_data = entry.analysis.result
                    if isinstance(analysis_data, str):
                        try:
                            analysis_data = json.loads(analysis_data)
                        except:
                            continue
                    
                    # Çarpıtmaları topla
                    distortions = analysis_data.get('distortions', [])
                    all_distortions.extend(distortions)
                    
                    # Risk seviyesi
                    risk = analysis_data.get('risk_level', 'belirsiz')
                    risk_levels.append(risk)
                    entry_texts.append(entry.text)
                
                # Kullanıcının seçtiği mood'u kullan
                if entry.mood_score is not None:
                    mood = self._score_to_mood(entry.mood_score)
                    mood_scores.append(mood)
            
            # İstatistikleri hesapla
            stats = {
                "entry_count": len(entries),
                "analyzed_entries": len([e for e in entries if e.analysis]),
                "total_distortions": len(all_distortions),
                "distortion_stats": self._analyze_distortions(all_distortions),
                "mood_analysis": self._analyze_mood(mood_scores, entries),
                "risk_analysis": self._analyze_risk(risk_levels),
                "progress_insights": self._generate_insights(all_distortions, mood_scores, entry_texts),
                "exercise_recommendations": self.generate_exercise_recommendations(all_distortions, mood_scores, risk_levels),
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            return {"error": f"İstatistik hesaplama hatası: {str(e)}"}
    
    def _analyze_distortions(self, distortions: List[Dict]) -> Dict[str, Any]:
        """Çarpıtma istatistiklerini analiz eder"""
        if not distortions:
            return {
                "total": 0,
                "most_common": [],
                "severity_distribution": {},
                "average_confidence": 0
            }
        
        # Çarpıtma türlerini say
        distortion_types = [d.get('type', 'bilinmeyen') for d in distortions]
        type_counts = Counter(distortion_types)
        
        # Şiddet dağılımı
        severity_counts = Counter([d.get('severity', 'belirsiz') for d in distortions])
        
        # Güven ortalaması
        confidences = [d.get('confidence', 0) for d in distortions if d.get('confidence')]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # En yaygın çarpıtmalar (top 5)
        most_common = [
            {"type": distortion_type, "count": count, "percentage": round((count / len(distortions)) * 100, 1)}
            for distortion_type, count in type_counts.most_common(5)
        ]
        
        return {
            "total": len(distortions),
            "most_common": most_common,
            "severity_distribution": dict(severity_counts),
            "average_confidence": round(avg_confidence, 2)
        }
    
    def _analyze_mood(self, mood_scores: List[str], entries: List[Entry]) -> Dict[str, Any]:
        """Ruh hali analizini yapar"""
        if not mood_scores:
            return {"error": "Ruh hali verisi bulunamadı"}
        
        mood_counts = Counter(mood_scores)
        total = len(mood_scores)
        
        # Ruh hali dağılımı
        mood_distribution = {
            mood: {
                "count": count,
                "percentage": round((count / total) * 100, 1)
            }
            for mood, count in mood_counts.items()
        }
        
        # Trend analizi (son 5 giriş)
        recent_moods = mood_scores[-5:] if len(mood_scores) >= 5 else mood_scores
        
        # Zaman serisi verisi (son 10 giriş için)
        mood_timeline = []
        
        # Mood score'u olan tüm girişleri al ve son 10'unu seç
        mood_entries = [e for e in entries if e.mood_score is not None]
        recent_entries = sorted(mood_entries, key=lambda x: x.created_at)[-10:]
        
        for entry in recent_entries:
            mood = self._score_to_mood(entry.mood_score)
            mood_timeline.append({
                "date": entry.created_at.strftime("%Y-%m-%d"),
                "mood": mood,
                "mood_score": entry.mood_score
            })
        
        # Trend hesaplama (son 5 giriş için)
        if len(mood_timeline) >= 2:
            # Son 5 girişi al (zaten tarih sırasında)
            recent_scores = [m["mood_score"] for m in mood_timeline[-5:]]
            if len(recent_scores) >= 2:
                trend_direction = "iyileşiyor" if recent_scores[-1] > recent_scores[0] else "kötüleşiyor" if recent_scores[-1] < recent_scores[0] else "stabil"
                trend_percentage = abs(recent_scores[-1] - recent_scores[0]) / max(recent_scores) * 100 if max(recent_scores) > 0 else 0
            else:
                trend_direction = "stabil"
                trend_percentage = 0
        else:
            trend_direction = "belirsiz"
            trend_percentage = 0
        
        return {
            "total_entries": total,
            "mood_distribution": mood_distribution,
            "recent_trend": recent_moods,
            "dominant_mood": mood_counts.most_common(1)[0][0] if mood_counts else "belirsiz",
            "mood_timeline": mood_timeline,
            "trend_direction": trend_direction,
            "trend_percentage": round(trend_percentage, 1)
        }
    
    def _mood_to_score(self, mood: str) -> int:
        """Ruh halini sayısal skora çevirir"""
        mood_scores = {
            # Yeni değerler
            "çok mutlu": 10,
            "mutlu": 8,
            "nötr": 5,
            "üzgün": 3,
            "çok üzgün": 1,
            # Eski değerler (geriye uyumluluk için)
            "çok iyi": 10,
            "iyi": 8,
            "orta": 5,
            "kötü": 3,
            "çok kötü": 1,
            # Varsayılan
            "belirsiz": 5
        }
        return mood_scores.get(mood.lower(), 5)
    
    def _score_to_mood(self, score: int) -> str:
        """Sayısal skoru ruh haline çevirir (1-5 arası)"""
        if score == 5:
            return "çok mutlu"
        elif score == 4:
            return "mutlu"
        elif score == 3:
            return "nötr"
        elif score == 2:
            return "üzgün"
        elif score == 1:
            return "çok üzgün"
        else:
            return "belirsiz"
    
    def _analyze_risk(self, risk_levels: List[str]) -> Dict[str, Any]:
        """Risk analizini yapar"""
        if not risk_levels:
            return {"error": "Risk verisi bulunamadı"}
        
        risk_counts = Counter(risk_levels)
        total = len(risk_levels)
        
        # Tüm risk seviyelerini say
        high_risk_count = risk_counts.get('yüksek', 0)
        medium_risk_count = risk_counts.get('orta', 0)
        low_risk_count = risk_counts.get('düşük', 0)
        unknown_risk_count = risk_counts.get('belirsiz', 0)
        
        # Yüksek risk yüzdesi
        high_risk_percentage = round((high_risk_count / total) * 100, 1) if total > 0 else 0
        
        # Orta ve üzeri risk yüzdesi (daha kapsamlı)
        medium_plus_risk_percentage = round(((high_risk_count + medium_risk_count) / total) * 100, 1) if total > 0 else 0
        
        return {
            "total_entries": total,
            "high_risk_entries": high_risk_count,
            "medium_risk_entries": medium_risk_count,
            "low_risk_entries": low_risk_count,
            "high_risk_percentage": high_risk_percentage,
            "medium_plus_risk_percentage": medium_plus_risk_percentage,
            "risk_distribution": dict(risk_counts),
            "trend": "azalıyor" if high_risk_count < total / 2 else "artıyor"
        }
    
    def _generate_insights(self, distortions: List[Dict], mood_scores: List[str], entry_texts: List[str]) -> Dict[str, Any]:
        """İçgörüler üretir"""
        insights = {
            "summary": "",
            "recommendations": [],
            "progress_indicators": {}
        }
        
        if not distortions:
            insights["summary"] = "Henüz bilişsel çarpıtma tespit edilmedi. Düşüncelerin dengeli görünüyor."
            return insights
        
        # En yaygın çarpıtma
        distortion_types = [d.get('type', 'bilinmeyen') for d in distortions]
        most_common = Counter(distortion_types).most_common(1)[0]
        
        # İyileşme önerileri
        recommendations = []
        if most_common[0] == "kişiselleştirme":
            recommendations.append("Sıkça kişiselleştirme çarpıtması yapıyorsun. Her olayın seninle ilgili olmadığını hatırla.")
        elif most_common[0] == "zihin okuma":
            recommendations.append("Zihin okuma çarpıtması yaygın. Başkalarının düşüncelerini tahmin etmek yerine açık iletişim kur.")
        elif most_common[0] == "felaketleştirme":
            recommendations.append("Felaketleştirme eğilimin var. Gelecekte olacakları tahmin etmek yerine şu ana odaklan.")
        
        # Genel özet
        total_distortions = len(distortions)
        avg_per_entry = total_distortions / len(entry_texts) if entry_texts else 0
        
        if avg_per_entry < 1:
            insights["summary"] = f"Genel olarak düşüncelerin dengeli. Ortalama {avg_per_entry:.1f} çarpıtma tespit edildi."
        elif avg_per_entry < 2:
            insights["summary"] = f"Bazı düşünce çarpıtmaları var. En yaygın: {most_common[0]} ({most_common[1]} kez)."
        else:
            insights["summary"] = f"Belirgin düşünce çarpıtmaları tespit edildi. En yaygın: {most_common[0]} ({most_common[1]} kez)."
        
        insights["recommendations"] = recommendations
        
        # İlerleme göstergeleri
        insights["progress_indicators"] = {
            "distortion_frequency": round(avg_per_entry, 2),
            "most_common_distortion": most_common[0],
            "total_entries_analyzed": len(entry_texts)
        }
        
        return insights
    
    def generate_exercise_recommendations(self, distortions: List[Dict], mood_scores: List[str], risk_levels: List[str]) -> Dict[str, Any]:
        """Kişiselleştirilmiş egzersiz önerileri üretir"""
        recommendations = {
            "daily_exercises": [],
            "weekly_challenges": [],
            "emergency_tools": [],
            "focus_areas": []
        }
        
        if not distortions:
            recommendations["daily_exercises"].append({
                "title": "Günlük Pozitif Düşünce Egzersizi",
                "description": "Her gün 3 pozitif düşünce yazın ve bunları tekrar edin.",
                "duration": "5 dakika",
                "difficulty": "kolay"
            })
            return recommendations
        
        # En yaygın çarpıtmalara göre öneriler
        distortion_types = [d.get('type', 'bilinmeyen') for d in distortions]
        most_common = Counter(distortion_types).most_common(3)
        
        # Kişiselleştirilmiş egzersizler
        for distortion_type, count in most_common:
            if distortion_type == "kişiselleştirme":
                recommendations["daily_exercises"].append({
                    "title": "Alternatif Açıklama Egzersizi",
                    "description": "Bir olay olduğunda, kendinizi suçlamadan önce 3 farklı açıklama düşünün.",
                    "duration": "10 dakika",
                    "difficulty": "orta",
                    "focus": "kişiselleştirme"
                })
                recommendations["focus_areas"].append("Kişiselleştirme çarpıtmasını azaltma")
            
            elif distortion_type == "zihin okuma":
                recommendations["daily_exercises"].append({
                    "title": "Açık İletişim Egzersizi",
                    "description": "Başkalarının düşüncelerini tahmin etmek yerine doğrudan sorun.",
                    "duration": "15 dakika",
                    "difficulty": "orta",
                    "focus": "zihin okuma"
                })
                recommendations["focus_areas"].append("Zihin okuma çarpıtmasını azaltma")
            
            elif distortion_type == "felaketleştirme":
                recommendations["daily_exercises"].append({
                    "title": "En Kötü Senaryo Egzersizi",
                    "description": "En kötü senaryoyu yazın, sonra bunun gerçekleşme olasılığını değerlendirin.",
                    "duration": "20 dakika",
                    "difficulty": "zor",
                    "focus": "felaketleştirme"
                })
                recommendations["focus_areas"].append("Felaketleştirme çarpıtmasını azaltma")
            
            elif distortion_type == "genelleme":
                recommendations["daily_exercises"].append({
                    "title": "İstisna Arama Egzersizi",
                    "description": "Genelleme yaptığınızda, bu genellemeye uymayan örnekler arayın.",
                    "duration": "10 dakika",
                    "difficulty": "orta",
                    "focus": "genelleme"
                })
                recommendations["focus_areas"].append("Genelleme çarpıtmasını azaltma")
        
        # Ruh haline göre öneriler
        mood_counts = Counter(mood_scores)
        dominant_mood = mood_counts.most_common(1)[0][0] if mood_counts else "belirsiz"
        
        if dominant_mood in ["kötü", "çok kötü"]:
            recommendations["emergency_tools"].append({
                "title": "5-4-3-2-1 Duyusal Egzersizi",
                "description": "5 şey gör, 4 şey dokun, 3 şey duy, 2 şey kokla, 1 şey tat.",
                "duration": "3 dakika",
                "when_to_use": "Anksiyete veya panik durumunda"
            })
            recommendations["daily_exercises"].append({
                "title": "Günlük Minnettarlık Egzersizi",
                "description": "Her gün 3 şey için minnettar olduğunuzu yazın.",
                "duration": "5 dakika",
                "difficulty": "kolay"
            })
        
        # Risk seviyesine göre öneriler
        risk_counts = Counter(risk_levels)
        high_risk_count = risk_counts.get('yüksek', 0)
        
        if high_risk_count > 0:
            recommendations["emergency_tools"].append({
                "title": "Güvenli Yer Egzersizi",
                "description": "Zihninizde güvenli bir yer hayal edin ve orada 5 dakika geçirin.",
                "duration": "5 dakika",
                "when_to_use": "Yüksek stres durumunda"
            })
        
        # Her zaman kullanılabilir acil durum araçları
        recommendations["emergency_tools"].append({
            "title": "Nefes Egzersizi",
            "description": "4 saniye nefes al, 4 saniye tut, 4 saniye ver. 5 kez tekrarla.",
            "duration": "2 dakika",
            "when_to_use": "Stres veya kaygı durumunda"
        })
        
        recommendations["emergency_tools"].append({
            "title": "Mantra Tekrarı",
            "description": "Kendinize 'Bu geçecek' veya 'Ben güçlüyüm' gibi pozitif bir cümle tekrarlayın.",
            "duration": "3 dakika",
            "when_to_use": "Olumsuz düşünceler geldiğinde"
        })
        
        # Haftalık zorluklar
        recommendations["weekly_challenges"].append({
            "title": "Çarpıtma Avcısı",
            "description": "Bu hafta günde en az 1 çarpıtmayı tespit edin ve alternatif düşünce bulun.",
            "duration": "Haftalık",
            "difficulty": "orta"
        })
        
        recommendations["weekly_challenges"].append({
            "title": "Mood Takipçisi",
            "description": "Her gün mood'unuzu 1-10 arası değerlendirin ve nedenlerini yazın.",
            "duration": "Haftalık",
            "difficulty": "kolay"
        })
        
        return recommendations
    
    async def generate_ai_insights(self, entry_texts: List[str], stats: Dict[str, Any]) -> str:
        """AI ile detaylı içgörüler üretir"""
        try:
            if not entry_texts:
                return "Henüz yeterli veri bulunamadı."
            
            # Son 5 girişi al
            recent_texts = entry_texts[-5:] if len(entry_texts) >= 5 else entry_texts
            combined_text = "\n\n".join(recent_texts)
            
            prompt = f"""
            Son günlük girişlerini analiz et ve kısa bir özet çıkar.
            
            Girişler:
            {combined_text}
            
            İstatistikler:
            - Toplam çarpıtma: {stats.get('total_distortions', 0)}
            - En yaygın çarpıtma: {stats.get('distortion_stats', {}).get('most_common', [{}])[0].get('type', 'bilinmeyen') if stats.get('distortion_stats', {}).get('most_common') else 'bilinmeyen'}
            - Ruh hali: {stats.get('mood_analysis', {}).get('dominant_mood', 'belirsiz')}
            
            Kısa ve yapıcı bir özet yaz (2-3 cümle). Doğrudan sen'e hitap et, "kullanıcı" kelimesini kullanma:
            """
            
            response = await self.cognitive_agent.llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            return f"AI analizi sırasında hata: {str(e)}"
