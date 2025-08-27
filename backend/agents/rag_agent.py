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

# ChromaDB entegrasyonu
from services.chroma_service import get_chroma_service

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

        # ChromaDB servisi
        try:
            self.chroma_service = get_chroma_service()
            self.use_chroma = True
            logger.info("ChromaDB servisi başarıyla başlatıldı")
        except Exception as e:
            logger.warning(f"ChromaDB başlatılamadı: {e}. Fallback moda geçiliyor.")
            self.chroma_service = None
            self.use_chroma = False

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

    async def get_therapy_techniques(self, distortion_type: str, user_context: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Belirli bir çarpıtma türü için terapi teknikleri önerir (ChromaDB + Statik)"""
        try:
            # Çarpıtma türünü normalize et
            normalized_type = self._normalize_distortion_type(distortion_type)
            
            # Hybrid yaklaşım: ChromaDB + Statik BDT_TECHNIQUES
            chroma_techniques = []
            static_techniques = []
            
            # 1. ChromaDB'den semantik arama
            if self.use_chroma and user_context:
                try:
                    chroma_techniques = await self.chroma_service.find_relevant_techniques(
                        query_text=user_context,
                        distortion_types=[normalized_type],
                        n_results=3
                    )
                    logger.info(f"ChromaDB'den {len(chroma_techniques)} teknik bulundu")
                except Exception as e:
                    logger.warning(f"ChromaDB arama hatası: {e}")
            
            # 2. Statik teknikleri al
            if normalized_type in BDT_TECHNIQUES:
                static_techniques = BDT_TECHNIQUES[normalized_type]["techniques"]
            else:
                return self._get_fallback_response(distortion_type)
            
            # 3. Teknikleri birleştir (ChromaDB öncelikli)
            combined_techniques = self._combine_techniques(chroma_techniques, static_techniques)
            
            # 4. Kişiselleştirme
            if user_context and user_id:
                personalized_response = await self._personalize_with_history(
                    techniques=combined_techniques,
                    user_context=user_context,
                    user_id=user_id,
                    distortion_type=normalized_type
                )
                return personalized_response
            elif user_context:
                # Basit kişiselleştirme
                personalized_response = await self._personalize_techniques(
                    {"techniques": combined_techniques, "name": BDT_TECHNIQUES[normalized_type]["name"]},
                    user_context, 
                    distortion_type
                )
                return personalized_response
            
            # 5. Temel yanıt
            base_techniques = BDT_TECHNIQUES[normalized_type]
            return {
                "distortion_type": normalized_type,
                "distortion_name": base_techniques["name"],
                "distortion_description": base_techniques["description"],
                "techniques": combined_techniques,
                "personalized_advice": f"{base_techniques['name']} çarpıtması için ChromaDB'den geliştirilmiş teknikler hazırladık.",
                "next_steps": [
                    "Önerilen tekniklerden birini seçin ve bugün uygulayın",
                    "Haftada en az 3 kez bu teknikleri tekrarlayın",
                    "İlerlemenizi günlüğünüzde takip edin",
                    "Zorlandığınızda bir uzmandan destek almayı düşünün"
                ],
                "source": "hybrid" if chroma_techniques else "static",
                "chroma_results": len(chroma_techniques),
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.exception("RAG teknikleri alma hatası")
            return self._get_fallback_response(distortion_type)

    async def get_multiple_techniques(self, distortion_types: List[str], user_context: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Birden fazla çarpıtma türü için teknikler önerir"""
        try:
            all_techniques = []
            for distortion_type in distortion_types:
                techniques = await self.get_therapy_techniques(distortion_type, user_context, user_id)
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
            "zihin_okuma": "zihin okuma",  # Alt çizgi formatı
            "genelleme": "genelleme",
            "kişiselleştirme": "kişiselleştirme",
            "kisisellestirme": "kişiselleştirme",
            "kisisellestirme": "kişiselleştirme",  # Alt çizgi formatı
            "etiketleme": "etiketleme",
            "ya hep ya hiç": "ya hep ya hiç",
            "ya hep ya hic": "ya hep ya hiç",
            "ya_hep_ya_hic": "ya hep ya hiç",  # Alt çizgi formatı
            "büyütme": "büyütme/küçültme",
            "buyutme": "büyütme/küçültme",
            "buyutme_kucultme": "büyütme/küçültme",  # Alt çizgi formatı
            "küçültme": "büyütme/küçültme",
            "kucultme": "büyütme/küçültme",
            "kehanetçilik": "kehanetçilik",
            "kehanetcilik": "kehanetçilik",
            "keyfi çıkarsama": "keyfi çıkarsama",
            "keyfi_cikarsama": "keyfi çıkarsama",  # Alt çizgi formatı
            "meli malı": "meli/malı düşünceleri",
            "meli/malı": "meli/malı düşünceleri",
            "meli-malı": "meli/malı düşünceleri",
            "meli_mali": "meli/malı düşünceleri"  # Alt çizgi formatı
        }
        
        normalized = mappings.get(type_lower, type_lower)
        return normalized

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

    # -----------------------------------------------------------------------------
    # ChromaDB Entegrasyon Metotları
    # -----------------------------------------------------------------------------
    
    def _combine_techniques(self, chroma_techniques: List[Dict], static_techniques: List[Dict]) -> List[Dict]:
        """ChromaDB ve statik teknikleri birleştirir"""
        try:
            combined = []
            
            # ChromaDB tekniklerini işle - gerçek BDT teknik içeriğini al
            for chroma_tech in chroma_techniques:
                metadata = chroma_tech.get('metadata', {})
                document_text = chroma_tech.get('text', '')
                
                # Document text'inden teknik bilgilerini çıkar
                technique_data = self._parse_technique_from_document(document_text, metadata)
                technique_data["source"] = "chromadb"
                technique_data["relevance_score"] = chroma_tech.get('relevance_score', 0.5)
                combined.append(technique_data)
            
            # Statik teknikleri ekle (ChromaDB sonuçları yeterli değilse)
            if len(combined) < 3:
                for static_tech in static_techniques[:3-len(combined)]:
                    static_tech_copy = static_tech.copy()
                    static_tech_copy["source"] = "static"
                    combined.append(static_tech_copy)
            
            return combined[:3]  # En fazla 3 teknik döndür
            
        except Exception as e:
            logger.error(f"Teknik birleştirme hatası: {e}")
            return static_techniques[:3]  # Fallback
    
    def _parse_technique_from_document(self, document_text: str, metadata: Dict) -> Dict:
        """ChromaDB document text'inden teknik bilgilerini çıkarır"""
        try:
            # Document text formatı:
            # """
            # Başlık: Teknik Başlığı
            # Açıklama: Teknik açıklaması
            # Egzersiz: Egzersiz açıklaması
            # Çarpıtma Türü: ...
            # """
            
            lines = document_text.strip().split('\n')
            technique_data = {
                "title": metadata.get('title', 'Bilinmeyen Teknik'),
                "description": "Teknik açıklaması bulunamadı",
                "exercise": "Egzersiz açıklaması bulunamadı",
                "duration": metadata.get('duration', '10-15 dakika'),
                "difficulty": metadata.get('difficulty', 'orta')
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('Başlık:'):
                    technique_data["title"] = line.replace('Başlık:', '').strip()
                elif line.startswith('Açıklama:'):
                    technique_data["description"] = line.replace('Açıklama:', '').strip()
                elif line.startswith('Egzersiz:'):
                    technique_data["exercise"] = line.replace('Egzersiz:', '').strip()
            
            # Metadata'dan gelen title'ı kullan (daha güvenilir)
            if metadata.get('title'):
                technique_data["title"] = metadata['title']
            
            # Eğer hala açıklama bulunamadıysa, statik BDT_TECHNIQUES'den al
            if technique_data["description"] == "Teknik açıklaması bulunamadı":
                distortion_type = metadata.get('distortion_type', '')
                technique_data = self._get_static_technique_backup(distortion_type, metadata.get('title', ''))
                technique_data["duration"] = metadata.get('duration', technique_data.get('duration', '10-15 dakika'))
                technique_data["difficulty"] = metadata.get('difficulty', technique_data.get('difficulty', 'orta'))
            
            return technique_data
            
        except Exception as e:
            logger.error(f"Document parsing hatası: {e}")
            # Fallback: metadata'dan ne varsa kullan
            return {
                "title": metadata.get('title', 'ChromaDB Tekniği'),
                "description": f"Bu teknik {metadata.get('distortion_type', 'bilişsel çarpıtma')} için önerilmiştir.",
                "exercise": "Günlük yazmaya devam edin ve bu durumu daha objektif açıdan değerlendirmeye çalışın.",
                "duration": metadata.get('duration', '10-15 dakika'),
                "difficulty": metadata.get('difficulty', 'orta')
            }
    
    def _get_static_technique_backup(self, distortion_type: str, title: str) -> Dict:
        """Statik BDT_TECHNIQUES'den backup teknik al"""
        try:
            if distortion_type in BDT_TECHNIQUES:
                techniques = BDT_TECHNIQUES[distortion_type]["techniques"]
                # Title'a en yakın tekniği bul
                for tech in techniques:
                    if title.lower() in tech.get("title", "").lower():
                        return tech.copy()
                # Bulamazsa ilk tekniği döndür
                if techniques:
                    return techniques[0].copy()
            
            # Hiçbir şey bulamazsa default
            return {
                "title": title or "Genel BDT Tekniği",
                "description": "Bu teknik düşünce kalıplarınızı iyileştirmenize yardımcı olur.",
                "exercise": "Durumu farklı açılardan değerlendirin ve daha dengeli düşünceler geliştirin.",
                "duration": "10-15 dakika",
                "difficulty": "orta"
            }
            
        except Exception as e:
            logger.error(f"Static backup hatası: {e}")
            return {
                "title": "Genel Teknik",
                "description": "Düşünce kalıplarınızı gözden geçirin.",
                "exercise": "Günlük yazılarınızda tekrar eden kalıpları fark edin.",
                "duration": "5-10 dakika",
                "difficulty": "kolay"
            }
    
    async def _personalize_with_history(
        self, 
        techniques: List[Dict], 
        user_context: str, 
        user_id: str, 
        distortion_type: str
    ) -> Dict[str, Any]:
        """Kullanıcının geçmiş verileriyle kişiselleştirme yapar"""
        try:
            # Kullanıcının geçmiş benzer deneyimlerini bul
            similar_entries = []
            user_patterns = {}
            
            if self.use_chroma:
                # Benzer geçmiş girişler
                similar_entries = await self.chroma_service.find_similar_entries(
                    user_id=user_id,
                    query_text=user_context,
                    distortion_type=distortion_type,
                    n_results=3
                )
                
                # Kullanıcı kalıpları
                user_patterns = await self.chroma_service.get_user_patterns(user_id)
            
            # Kişiselleştirilmiş tavsiye oluştur
            personalized_advice = await self._generate_personalized_advice(
                user_context=user_context,
                distortion_type=distortion_type,
                similar_entries=similar_entries,
                user_patterns=user_patterns,
                techniques=techniques
            )
            
            base_info = BDT_TECHNIQUES.get(distortion_type, {})
            
            return {
                "distortion_type": distortion_type,
                "distortion_name": base_info.get("name", distortion_type),
                "distortion_description": base_info.get("description", ""),
                "techniques": techniques,
                "personalized_advice": personalized_advice,
                "similar_experiences_count": len(similar_entries),
                "user_patterns": user_patterns.get('most_common_distortions', [])[:3] if user_patterns else [],
                "next_steps": self._generate_personalized_next_steps(user_patterns, techniques),
                "source": "personalized_chromadb",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Kişiselleştirme hatası: {e}")
            # Fallback: basit kişiselleştirme
            return await self._personalize_techniques(
                {"techniques": techniques, "name": BDT_TECHNIQUES.get(distortion_type, {}).get("name", "")},
                user_context,
                distortion_type
            )
    
    async def _generate_personalized_advice(
        self,
        user_context: str,
        distortion_type: str,
        similar_entries: List[Dict],
        user_patterns: Dict,
        techniques: List[Dict]
    ) -> str:
        """LLM ile kişiselleştirilmiş tavsiye oluşturur"""
        try:
            if not self.llm:
                return f"{distortion_type} çarpıtması için kişiselleştirilmiş teknikler hazırlandı."
            
            # Kontext hazırla
            context_parts = [f"Mevcut durum: {user_context}"]
            
            if similar_entries:
                context_parts.append(f"Benzer geçmiş deneyimler: {len(similar_entries)} adet")
            
            if user_patterns and user_patterns.get('most_common_distortions'):
                common = user_patterns['most_common_distortions'][:3]
                context_parts.append(f"En sık karşılaştığınız çarpıtmalar: {', '.join([c[0] for c in common])}")
            
            prompt = f"""
            Kullanıcı profili: {' | '.join(context_parts)}
            Çarpıtma türü: {distortion_type}
            Önerilen teknik sayısı: {len(techniques)}
            
            Bu kullanıcı için kişiselleştirilmiş, destekleyici ve cesaret verici bir tavsiye yazın.
            - Kullanıcının durumuna özel olarak konuşun
            - Geçmiş deneyimlerinden faydalanın
            - Pratik ve uygulanabilir olsun
            - 2-3 cümle ile sınırlayın
            - Türkçe yazın ve "sen" hitabı kullanın
            """
            
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Kişiselleştirilmiş tavsiye oluşturma hatası: {e}")
            return f"{distortion_type} çarpıtması için geçmiş deneyimlerinize dayalı özel teknikler hazırladık."
    
    def _generate_personalized_next_steps(self, user_patterns: Dict, techniques: List[Dict]) -> List[str]:
        """Kullanıcı kalıplarına göre sonraki adımları oluşturur"""
        try:
            base_steps = [
                "Bu kişiselleştirilmiş tavsiyeyi günlüğünüze not edin",
                "En uygun tekniği seçip bu hafta düzenli uygulayın"
            ]
            
            # Kullanıcı kalıplarına göre ek adımlar
            if user_patterns:
                total_analyses = user_patterns.get('total_analyses', 0)
                
                if total_analyses < 5:
                    base_steps.append("Daha fazla analiz için günlük yazmaya devam edin")
                elif total_analyses >= 10:
                    base_steps.append("İlerleme kaydınızı gözden geçirin ve başarılarınızı kutlayın")
                
                # Risk seviyesi kontrolü
                risk_dist = user_patterns.get('risk_level_distribution', {})
                if risk_dist.get('high', 0) > 0:
                    base_steps.append("Yüksek risk dönemlerinde profesyonel destek almayı değerlendirin")
            
            base_steps.append("İlerlemenizi takip etmek için günlük yazmaya devam edin")
            
            return base_steps
            
        except Exception as e:
            logger.error(f"Kişiselleştirilmiş adım oluşturma hatası: {e}")
            return [
                "Önerilen tekniklerden birini seçin ve bugün uygulayın",
                "Haftada en az 3 kez bu teknikleri tekrarlayın",
                "İlerlemenizi günlüğünüzde takip edin"
            ]
    
    # -----------------------------------------------------------------------------
    # ChromaDB Data Management
    # -----------------------------------------------------------------------------
    
    async def add_user_entry_to_chroma(self, entry_id: str, user_id: str, text: str, analysis_result: Dict[str, Any]) -> bool:
        """Kullanıcı girişini ChromaDB'ye ekler"""
        try:
            if not self.use_chroma:
                return False
                
            return await self.chroma_service.add_user_entry(
                entry_id=str(entry_id),
                user_id=str(user_id),
                text=text,
                analysis_result=analysis_result
            )
            
        except Exception as e:
            logger.error(f"ChromaDB'ye entry ekleme hatası: {e}")
            return False
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının düşünce kalıpları hakkında içgörüler"""
        try:
            if not self.use_chroma:
                return {"message": "ChromaDB mevcut değil"}
                
            return await self.chroma_service.get_user_patterns(user_id)
            
        except Exception as e:
            logger.error(f"Kullanıcı içgörüleri hatası: {e}")
            return {"error": "İçgörüler alınamadı"}
