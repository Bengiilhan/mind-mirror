"""
RAG Agent - Kişiselleştirilmiş Terapi Teknikleri için Retrieval-Augmented Generation
Bu agent, kullanıcının bilişsel çarpıtma türüne göre özel BDT teknikleri ve egzersizler önerir.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# -----------------------------------------------------------------------------
# Logging konfigürasyonu
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# BDT Teknikleri Veritabanı (Basit JSON formatında)
# -----------------------------------------------------------------------------
BDT_TECHNIQUES = {
    "felaketleştirme": {
        "name": "Felaketleştirme",
        "description": "Gelecekte olabilecek en kötü senaryoları düşünme eğilimi",
        "techniques": [
            {
                "title": "Olasılık Değerlendirmesi",
                "description": "Korktuğunuz durumun gerçekleşme olasılığını yüzde olarak değerlendirin",
                "exercise": "Korktuğunuz durumu yazın ve gerçekleşme olasılığını %0-100 arasında tahmin edin. Sonra bu olasılığı nasıl azaltabileceğinizi düşünün.",
                "duration": "5-10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Alternatif Senaryolar",
                "description": "En kötü senaryo dışındaki olasılıkları da düşünün",
                "exercise": "Korktuğunuz durum için 3 farklı senaryo yazın: en kötü, en iyi ve en muhtemel olan.",
                "duration": "10-15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Kanıt Toplama",
                "description": "Korkularınızı destekleyen ve çürüten kanıtları listeleyin",
                "exercise": "Korktuğunuz durumun gerçekleşeceğine dair kanıtları ve gerçekleşmeyeceğine dair kanıtları iki sütun halinde yazın.",
                "duration": "15-20 dakika",
                "difficulty": "orta"
            }
        ]
    },
    "zihin okuma": {
        "name": "Zihin Okuma",
        "description": "Başkalarının ne düşündüğünü bildiğinizi varsayma",
        "techniques": [
            {
                "title": "Açık İletişim",
                "description": "Varsayımlarınızı doğrulamak için sorular sorun",
                "exercise": "Birinin sizin hakkında ne düşündüğünü tahmin ettiğinizde, doğrudan o kişiye sorun: 'Seninle ilgili bir endişem var, konuşabilir miyiz?'",
                "duration": "5 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Alternatif Açıklamalar",
                "description": "Başkalarının davranışları için farklı nedenler düşünün",
                "exercise": "Birinin size karşı olumsuz davrandığını düşündüğünüzde, bunun 3 farklı nedeni olabileceğini yazın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Kendinizi Başkasının Yerine Koyma",
                "description": "Olayları başka birinin perspektifinden değerlendirin",
                "exercise": "Yaşadığınız durumu bir arkadaşınızın yaşadığını düşünün. Ona nasıl tavsiye verirdiniz?",
                "duration": "15 dakika",
                "difficulty": "orta"
            }
        ]
    },
    "genelleme": {
        "name": "Genelleme",
        "description": "Tek bir olaydan genel sonuçlar çıkarma",
        "techniques": [
            {
                "title": "İstisnaları Bulma",
                "description": "Genellemenizin geçerli olmadığı durumları düşünün",
                "exercise": "Yaptığınız genellemeyi yazın ve bunun geçerli olmadığı 3 örnek bulun.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Daha Dengeli Dil",
                "description": "Aşırı genellemeler yerine daha spesifik ifadeler kullanın",
                "exercise": "Kullandığınız 'her zaman', 'hiçbir zaman', 'herkes', 'hiç kimse' gibi kelimeleri daha spesifik ifadelerle değiştirin.",
                "duration": "5-10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Veri Toplama",
                "description": "Genellemenizi test etmek için veri toplayın",
                "exercise": "Genellemenizi test etmek için 1 hafta boyunca günlük tutun ve kaç kez doğru/yanlış olduğunu kaydedin.",
                "duration": "1 hafta",
                "difficulty": "zor"
            }
        ]
    },
    "kişiselleştirme": {
        "name": "Kişiselleştirme",
        "description": "Her şeyi kendinize mal etme eğilimi",
        "techniques": [
            {
                "title": "Sorumluluk Paylaşımı",
                "description": "Bir durumda sizin ve başkalarının payını değerlendirin",
                "exercise": "Kendinizi suçladığınız bir durumu yazın ve sorumluluğun yüzde kaçının size ait olduğunu hesaplayın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Dış Faktörleri Düşünme",
                "description": "Durumun oluşmasında rol oynayan diğer faktörleri listeleyin",
                "exercise": "Kendinizi suçladığınız durumun oluşmasında rol oynayan 5 farklı faktörü yazın.",
                "duration": "15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Başkasının Perspektifi",
                "description": "Aynı durumu başka biri yaşasaydı ne düşünürdünüz?",
                "exercise": "Kendinizi suçladığınız durumu bir arkadaşınızın yaşadığını düşünün. Onu nasıl teselli ederdiniz?",
                "duration": "10 dakika",
                "difficulty": "kolay"
            }
        ]
    },
    "etiketleme": {
        "name": "Etiketleme",
        "description": "Kendinizi veya başkalarını aşırı genel etiketlerle tanımlama",
        "techniques": [
            {
                "title": "Davranış Odaklı Dil",
                "description": "Kişilik etiketleri yerine spesifik davranışları tanımlayın",
                "exercise": "Kullandığınız etiketleri yazın ve bunları spesifik davranışlarla değiştirin. Örn: 'Aptalım' yerine 'Bu konuda hata yaptım'.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Çok Yönlü Değerlendirme",
                "description": "Kendinizi farklı alanlarda değerlendirin",
                "exercise": "Kendinizi 5 farklı alanda (iş, ilişkiler, sağlık, hobi, öğrenme) 1-10 arası puanlayın.",
                "duration": "15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Gelişim Odaklı Düşünme",
                "description": "Sabit etiketler yerine gelişim potansiyeline odaklanın",
                "exercise": "Kendinizi etiketlediğiniz bir özelliği nasıl geliştirebileceğinizi yazın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            }
        ]
    },
    "ya hep ya hiç": {
        "name": "Ya Hep Ya Hiç Düşüncesi",
        "description": "Durumları sadece siyah veya beyaz olarak görme",
        "techniques": [
            {
                "title": "Gri Tonları Bulma",
                "description": "Siyah-beyaz düşüncelerinizdeki gri alanları keşfedin",
                "exercise": "Ya hep ya hiç düşündüğünüz bir durumu yazın ve bu durumun farklı seviyelerini 1-10 arası puanlayın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Kısmi Başarıları Tanıma",
                "description": "Mükemmel olmayan başarıları da değerli görün",
                "exercise": "Son zamanlarda %100 başarılı olmadığınız ama yine de değerli olan 3 şeyi yazın.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Öğrenme Odaklı Düşünme",
                "description": "Başarısızlıkları öğrenme fırsatı olarak görün",
                "exercise": "Son 'başarısızlık' olarak gördüğünüz bir durumdan öğrendiğiniz 3 şeyi yazın.",
                "duration": "15 dakika",
                "difficulty": "orta"
            }
        ]
    },
    "büyütme/küçültme": {
        "name": "Büyütme/Küçültme",
        "description": "Olumsuzları büyütme, olumluları küçültme",
        "techniques": [
            {
                "title": "Dengeli Değerlendirme",
                "description": "Olumlu ve olumsuz yönleri eşit ağırlıkta değerlendirin",
                "exercise": "Bir durumun olumlu ve olumsuz yönlerini iki sütun halinde yazın ve her birine 1-10 arası puan verin.",
                "duration": "15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Perspektif Alma",
                "description": "Durumu farklı açılardan değerlendirin",
                "exercise": "Yaşadığınız durumu 1 yıl sonra nasıl göreceğinizi yazın.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Kanıt Toplama",
                "description": "Olumlu ve olumsuz kanıtları eşit şekilde toplayın",
                "exercise": "Kendinizle ilgili olumlu ve olumsuz kanıtları listeleyin ve hangisinin daha ağır bastığını değerlendirin.",
                "duration": "20 dakika",
                "difficulty": "zor"
            }
        ]
    },
    "kehanetçilik": {
        "name": "Kehanetçilik",
        "description": "Geleceği tahmin ettiğinizi varsayma",
        "techniques": [
            {
                "title": "Tahmin Testi",
                "description": "Geçmiş tahminlerinizin doğruluğunu kontrol edin",
                "exercise": "Son 1 ay içinde yaptığınız 3 tahmini yazın ve hangilerinin doğru çıktığını kontrol edin.",
                "duration": "15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Alternatif Sonuçlar",
                "description": "Tahmin ettiğiniz sonuç dışındaki olasılıkları düşünün",
                "exercise": "Korktuğunuz sonucun gerçekleşmeme ihtimalini yüzde olarak hesaplayın ve bu durumda ne yapacağınızı planlayın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Şu Ana Odaklanma",
                "description": "Gelecek endişeleri yerine şu anki duruma odaklanın",
                "exercise": "Şu anda kontrol edebileceğiniz 3 şeyi yazın ve bunlara odaklanın.",
                "duration": "5 dakika",
                "difficulty": "kolay"
            }
        ]
    },
    "keyfi çıkarsama": {
        "name": "Keyfi Çıkarsama",
        "description": "Kanıt olmadan sonuçlar çıkarma",
        "techniques": [
            {
                "title": "Kanıt Değerlendirmesi",
                "description": "Vardığınız sonucu destekleyen kanıtları listeleyin",
                "exercise": "Bir sonuca vardığınızda, bu sonucu destekleyen somut kanıtları yazın.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Alternatif Açıklamalar",
                "description": "Aynı durum için farklı açıklamalar düşünün",
                "exercise": "Vardığınız sonuç dışında, durumu açıklayabilecek 3 farklı neden yazın.",
                "duration": "15 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Soru Sorma",
                "description": "Sonuçlarınızı test etmek için sorular sorun",
                "exercise": "Vardığınız sonucu test etmek için kendinize 3 soru sorun.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            }
        ]
    },
    "meli/malı düşünceleri": {
        "name": "-meli/-malı Düşünceleri",
        "description": "Kendiniz ve başkaları için katı kurallar koyma",
        "techniques": [
            {
                "title": "Esnek Kurallar",
                "description": "Katı kurallarınızı daha esnek hale getirin",
                "exercise": "Kullandığınız 'meli/malı' ifadelerini yazın ve bunları daha esnek alternatiflerle değiştirin.",
                "duration": "10 dakika",
                "difficulty": "kolay"
            },
            {
                "title": "Standart Belirleme",
                "description": "Gerçekçi standartlar belirleyin",
                "exercise": "Kendiniz için belirlediğiniz bir standardı yazın ve bunun gerçekçi olup olmadığını değerlendirin.",
                "duration": "10 dakika",
                "difficulty": "orta"
            },
            {
                "title": "Kendine Şefkat",
                "description": "Kendinize karşı daha anlayışlı olun",
                "exercise": "Bir arkadaşınızın aynı durumu yaşadığını düşünün. Ona nasıl davranırdınız?",
                "duration": "10 dakika",
                "difficulty": "orta"
            }
        ]
    }
}

# -----------------------------------------------------------------------------
# Pydantic Modelleri
# -----------------------------------------------------------------------------
class TherapyTechnique(BaseModel):
    """Terapi tekniği modeli"""
    title: str = Field(description="Tekniğin başlığı")
    description: str = Field(description="Tekniğin açıklaması")
    exercise: str = Field(description="Pratik egzersiz")
    duration: str = Field(description="Tahmini süre")
    difficulty: str = Field(description="Zorluk seviyesi (kolay/orta/zor)")

class RAGResponse(BaseModel):
    """RAG yanıt modeli"""
    distortion_type: str = Field(description="Çarpıtma türü")
    distortion_name: str = Field(description="Çarpıtmanın tam adı")
    distortion_description: str = Field(description="Çarpıtmanın açıklaması")
    techniques: List[TherapyTechnique] = Field(description="Önerilen teknikler")
    personalized_advice: str = Field(description="Kişiselleştirilmiş tavsiye")
    next_steps: List[str] = Field(description="Sonraki adımlar")

# -----------------------------------------------------------------------------
# RAG Agent Sınıfı
# -----------------------------------------------------------------------------
class RAGAgent:
    """Kişiselleştirilmiş terapi teknikleri için RAG agent"""

    def __init__(self) -> None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("OPENAI_API_KEY bulunamadı. RAG sistemi API key olmadan çalışacak.")
            self.llm = None
            self.structured_llm = None
        else:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    openai_api_key=api_key,
                    temperature=0.3,
                    max_tokens=1000,
                    timeout=20,
                    max_retries=2,
                )
                self.structured_llm = self.llm.with_structured_output(RAGResponse)
            except Exception as e:
                logger.error(f"LLM başlatma hatası: {e}")
                self.llm = None
                self.structured_llm = None

    async def get_therapy_techniques(self, distortion_type: str, user_context: Optional[str] = None) -> Dict[str, Any]:
        """Belirli bir çarpıtma türü için terapi teknikleri önerir"""
        try:
            # Çarpıtma türünü normalize et
            normalized_type = self._normalize_distortion_type(distortion_type)
            
            if normalized_type not in BDT_TECHNIQUES:
                return self._get_fallback_response(distortion_type)

            # Temel teknikleri al
            base_techniques = BDT_TECHNIQUES[normalized_type]
            
            # Kullanıcı bağlamı varsa kişiselleştir
            if user_context:
                personalized_response = await self._personalize_techniques(
                    base_techniques, user_context, distortion_type
                )
                return personalized_response
            
            # Temel yanıtı döndür
            return {
                "distortion_type": normalized_type,
                "distortion_name": base_techniques["name"],
                "distortion_description": base_techniques["description"],
                "techniques": base_techniques["techniques"],
                "personalized_advice": f"{base_techniques['name']} çarpıtması için özel teknikler hazırladık. Bu teknikleri günlük rutininize ekleyerek daha sağlıklı düşünce kalıpları geliştirebilirsiniz.",
                "next_steps": [
                    "Önerilen tekniklerden birini seçin ve bugün uygulayın",
                    "Haftada en az 3 kez bu teknikleri tekrarlayın",
                    "İlerlemenizi günlüğünüzde takip edin",
                    "Zorlandığınızda bir uzmandan destek almayı düşünün"
                ],
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception("RAG teknikleri alma hatası")
            return self._get_fallback_response(distortion_type)

    async def get_multiple_techniques(self, distortion_types: List[str], user_context: Optional[str] = None) -> Dict[str, Any]:
        """Birden fazla çarpıtma türü için teknikler önerir"""
        try:
            all_techniques = []
            for distortion_type in distortion_types:
                techniques = await self.get_therapy_techniques(distortion_type, user_context)
                all_techniques.append(techniques)

            return {
                "multiple_distortions": True,
                "techniques": all_techniques,
                "summary": f"{len(distortion_types)} farklı çarpıtma türü için teknikler hazırlandı",
                "recommendation": "En sık karşılaştığınız çarpıtma türüne odaklanarak başlayın",
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception("Çoklu RAG teknikleri alma hatası")
            return {"error": "Teknikler alınırken hata oluştu"}

    def _normalize_distortion_type(self, distortion_type: str) -> str:
        """Çarpıtma türünü normalize eder"""
        type_lower = distortion_type.lower().strip()
        
        # Türkçe eşleştirmeler
        mappings = {
            "felaketleştirme": "felaketleştirme",
            "felaketlestirme": "felaketleştirme",
            "zihin okuma": "zihin okuma",
            "genelleme": "genelleme",
            "kişiselleştirme": "kişiselleştirme",
            "kisisellestirme": "kişiselleştirme",
            "etiketleme": "etiketleme",
            "ya hep ya hiç": "ya hep ya hiç",
            "ya hep ya hic": "ya hep ya hiç",
            "büyütme": "büyütme/küçültme",
            "buyutme": "büyütme/küçültme",
            "küçültme": "büyütme/küçültme",
            "kucultme": "büyütme/küçültme",
            "kehanetçilik": "kehanetçilik",
            "kehanetcilik": "kehanetçilik",
            "keyfi çıkarsama": "keyfi çıkarsama",
            "keyfi cikarsama": "keyfi çıkarsama",
            "meli malı": "meli/malı düşünceleri",
            "meli/malı": "meli/malı düşünceleri",
            "meli-malı": "meli/malı düşünceleri"
        }
        
        return mappings.get(type_lower, type_lower)

    async def _personalize_techniques(self, base_techniques: Dict, user_context: str, distortion_type: str) -> Dict[str, Any]:
        """Kullanıcı bağlamına göre teknikleri kişiselleştirir"""
        try:
            prompt = f"""
            Kullanıcının günlük yazısı: {user_context}
            
            Çarpıtma türü: {distortion_type}
            
            Bu kullanıcı için kişiselleştirilmiş bir tavsiye yaz. Kullanıcının durumuna özel olarak:
            1. Daha anlayışlı ve destekleyici bir ton kullan
            2. Kullanıcının yaşadığı spesifik duruma atıfta bulun
            3. Pratik ve uygulanabilir öneriler ver
            4. Türkçe yaz ve doğrudan kullanıcıya hitap et (sen/siz)
            
            Yanıtını 2-3 cümle ile sınırla.
            """
            
            response = await self.llm.ainvoke(prompt)
            personalized_advice = response.content.strip()
            
            return {
                "distortion_type": distortion_type,
                "distortion_name": base_techniques["name"],
                "distortion_description": base_techniques["description"],
                "techniques": base_techniques["techniques"],
                "personalized_advice": personalized_advice,
                "next_steps": [
                    "Bu kişiselleştirilmiş tavsiyeyi günlüğünüze not edin",
                    "Önerilen tekniklerden en uygun olanını seçin",
                    "Hafta boyunca bu tekniği düzenli olarak uygulayın",
                    "İlerlemenizi takip etmek için günlük tutmaya devam edin"
                ],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Kişiselleştirme hatası: {e}")
            # Fallback: temel yanıtı döndür
            return {
                "distortion_type": distortion_type,
                "distortion_name": base_techniques["name"],
                "distortion_description": base_techniques["description"],
                "techniques": base_techniques["techniques"],
                "personalized_advice": f"{base_techniques['name']} çarpıtması için özel teknikler hazırladık.",
                "next_steps": [
                    "Önerilen tekniklerden birini seçin ve bugün uygulayın",
                    "Haftada en az 3 kez bu teknikleri tekrarlayın",
                    "İlerlemenizi günlüğünüzde takip edin"
                ],
                "generated_at": datetime.now().isoformat()
            }

    def _get_fallback_response(self, distortion_type: str) -> Dict[str, Any]:
        """Bilinmeyen çarpıtma türü için fallback yanıt"""
        return {
            "distortion_type": distortion_type,
            "distortion_name": "Bilinmeyen Çarpıtma",
            "distortion_description": "Bu çarpıtma türü için henüz teknik hazırlanmamış",
            "techniques": [
                {
                    "title": "Genel BDT Tekniği",
                    "description": "Düşünce kalıplarınızı gözlemleyin",
                    "exercise": "Günlük yazınızda hangi düşünce kalıplarının tekrar ettiğini not edin.",
                    "duration": "10 dakika",
                    "difficulty": "kolay"
                }
            ],
            "personalized_advice": "Bu çarpıtma türü için özel teknikler geliştiriyoruz. Şimdilik genel BDT tekniklerini kullanabilirsiniz.",
            "next_steps": [
                "Günlük yazmaya devam edin",
                "Düşünce kalıplarınızı gözlemleyin",
                "Bir uzmandan destek almayı düşünün"
            ],
            "generated_at": datetime.now().isoformat()
        }

    def get_available_distortions(self) -> List[str]:
        """Mevcut çarpıtma türlerini döndürür"""
        return list(BDT_TECHNIQUES.keys())

    def get_technique_summary(self) -> Dict[str, int]:
        """Teknik özeti döndürür"""
        summary = {}
        for distortion_type, data in BDT_TECHNIQUES.items():
            summary[data["name"]] = len(data["techniques"])
        return summary
