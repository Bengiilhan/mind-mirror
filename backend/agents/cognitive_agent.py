"""
Cognitive Analysis Agent - Bilişsel Çarpıtma Tespiti için LangChain Agent
Bu agent, kullanıcının günlük yazılarını analiz ederek bilişsel çarpıtmaları tespit eder
ve alternatif düşünceler üretir.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough

# Logging konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CognitiveDistortion(BaseModel):
    """Bilişsel çarpıtma modeli"""
    type: str = Field(description="Çarpıtma türü (örn: felaketleştirme, zihin okuma, genelleme)")
    sentence: str = Field(description="Çarpıtma içeren cümle")
    explanation: str = Field(description="Neden bu çarpıtma olduğuna dair açıklama")
    alternative: str = Field(description="Daha sağlıklı alternatif düşünce")
    severity: Optional[str] = Field(default="orta", description="Çarpıtmanın şiddeti (düşük/orta/yüksek)")
    confidence: Optional[float] = Field(default=0.7, description="Tespit güvenilirliği (0-1 arası)")

class AnalysisResult(BaseModel):
    """Analiz sonucu modeli"""
    distortions: List[CognitiveDistortion] = Field(description="Tespit edilen bilişsel çarpıtmalar")
    risk_level: str = Field(description="Risk seviyesi (düşük/orta/yüksek)")
    recommendations: Optional[List[str]] = Field(default=[], description="Genel öneriler")
    analysis_timestamp: Optional[str] = Field(default=None, description="Analiz zamanı")

class CognitiveAnalysisAgent:
    """Bilişsel çarpıtma analizi için LangChain tabanlı agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",  # En güncel ve güvenilir model
            temperature=0.1,  # Daha düşük temperature = daha hızlı
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=1500,  # Biraz daha token
            request_timeout=30  # Biraz daha uzun timeout
        )
        
        # Çıktı parser
        self.output_parser = JsonOutputParser(pydantic_object=AnalysisResult)
        
        # Sistem prompt'u - optimize edilmiş
        self.system_prompt = """BDT uzmanı olarak günlük yazısını analiz et. Bilişsel çarpıtmaları tespit et.

        Çarpıtma türleri: Felaketleştirme, Zihin okuma, Genelleme, Kişiselleştirme, Etiketleme, Ya hep ya hiç, Büyütme/küçültme, Kehanetçilik, Keyfi çıkarsama, -meli/-malı düşünceleri.

        Analiz yaparken:
        1. Metni dikkatlice oku ve olumsuz düşünceleri tespit et
        2. Her çarpıtma için türünü belirle
        3. Şiddet seviyesini değerlendir
        4. Güvenilir alternatif düşünceler öner
        5. Risk seviyesini değerlendir
        6. Yapıcı ve destekleyici bir ton kullan.

        JSON formatında yanıt ver:
        {{
            "distortions": [
                {{
                    "type": "çarpıtma_türü",
                    "sentence": "ilgili_cümle",
                    "explanation": "Bu düşünce şu nedenle bir çarpıtmadır...",
                    "alternative": "alternatif_düşünce",
                    "severity": "düşük/orta/yüksek",
                    "confidence": 0.8
                }}
            ],
            "risk_level": "düşük/orta/yüksek",
            "recommendations": ["öneri1", "öneri2"]
        }}
        """
        
        # Ana analiz prompt'u - ultra optimize edilmiş
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Analiz et:\n{text}")
        ])
        
        # Memory sistemi
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Basit analiz için doğrudan LLM kullan
        self._setup_simple_analysis()
    
    def _setup_simple_analysis(self):
        """Basit analiz için gerekli ayarları yapar"""
        pass
    
    async def analyze_entry(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Günlük yazısını analiz eder"""
        try:
            # Ana analiz - risk değerlendirmesi ve öneriler dahil
            analysis_result = await self._analyze_text_async(text)
            
            # Sonuçları birleştir
            final_result = {
                **analysis_result,
                "analysis_timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Memory'ye kaydet (opsiyonel - hız için kaldırılabilir)
            # self.memory.save_context(
            #     {"input": f"Analiz: {text[:100]}..."},
            #     {"output": json.dumps(final_result, ensure_ascii=False)}
            # )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return {
                "error": "Analiz sırasında hata oluştu",
                "details": str(e),
                "distortions": [],
                "risk_level": "belirsiz",
                "recommendations": ["Lütfen daha sonra tekrar deneyin."],
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    # Risk değerlendirmesi artık ana analiz içinde yapılıyor
    # async def _assess_risk_async(self, text: str) -> str:
    #     """Risk değerlendirmesi yapar"""
    #     try:
    #         risk_prompt = f"""
    #         Aşağıdaki metni oku ve risk seviyesini değerlendir:
    #         - Düşük risk: Normal günlük yazısı
    #         - Orta risk: Depresif veya kaygılı düşünceler
    #         - Yüksek risk: İntihar düşüncesi, ciddi kriz belirtileri
    #         
    #         Metin: {text}
    #         
    #         Sadece risk seviyesini döndür: "düşük", "orta" veya "yüksek"
    #         """
    #         
    #         response = await self.llm.ainvoke(risk_prompt)
    #         return response.content.strip().lower()
    #     except:
    #         return "belirsiz"
    
    async def _analyze_text_async(self, text: str) -> Dict[str, Any]:
        """Metni analiz eder - ultra optimize edilmiş"""
        try:
            # Sistem prompt'u ile birlikte LLM çağrısı
            full_prompt = f"""BDT uzmanı. Günlük yazısını analiz et. Çarpıtmaları tespit et.

Çarpıtma türleri: Felaketleştirme, Zihin okuma, Genelleme, Kişiselleştirme, Etiketleme, Ya hep ya hiç, Büyütme/küçültme, Kehanetçilik, Keyfi çıkarsama, -meli/-malı düşünceleri.

KURALLAR: Doğrudan kullanıcıya hitap et (sen, siz). İntihar düşüncesi varsa risk="yüksek" yap.

Metin: {text}

SADECE JSON formatında yanıt ver, başka hiçbir şey ekleme:
{{
    "distortions": [
        {{
            "type": "çarpıtma_türü",
            "sentence": "ilgili_cümle",
            "explanation": "Bu düşünce şu nedenle çarpıtmadır...",
            "alternative": "alternatif_düşünce",
            "severity": "düşük/orta/yüksek",
            "confidence": 0.8
        }}
    ],
    "risk_level": "düşük/orta/yüksek",
    "recommendations": ["öneri1", "öneri2"]
}}"""

            # LLM çağrısı
            response = await self.llm.ainvoke(full_prompt)
            
            # JSON parse
            try:
                return json.loads(response.content)
            except:
                # Fallback: JSON çıkar
                json_data = self._extract_json_from_text(response.content)
                return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            logger.error(f"LLM yanıtı: {response.content if 'response' in locals() else 'Yanıt yok'}")
            return {
                "distortions": [
                    {
                        "type": "Genelleme",
                        "sentence": text[:100] + "..." if len(text) > 100 else text,
                        "explanation": "Metin analiz edilemedi, teknik bir hata oluştu",
                        "alternative": "Daha sonra tekrar deneyin",
                        "severity": "düşük",
                        "confidence": 0.1
                    }
                ],
                "risk_level": "belirsiz",
                "recommendations": ["Analiz sırasında teknik bir hata oluştu. Lütfen daha sonra tekrar deneyin."]
            }
    
    def _extract_json_from_text(self, text: str) -> str:
        """Metinden JSON çıkarır - geliştirilmiş"""
        try:
            logger.info(f"JSON çıkarma başlatılıyor. Metin: {text[:200]}...")
            
            # İlk deneme: Basit JSON arama
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            
            if json_start != -1 and json_end != 0:
                json_data = text[json_start:json_end].strip()
                # JSON geçerliliğini test et
                json.loads(json_data)
                logger.info(f"JSON bulundu (basit arama): {json_data[:100]}...")
                return json_data
            
            # İkinci deneme: Temizleme
            cleaned_text = text.replace('\n', ' ').replace('\r', ' ').strip()
            json_start = cleaned_text.find("{")
            json_end = cleaned_text.rfind("}") + 1
            
            if json_start != -1 and json_end != 0:
                json_data = cleaned_text[json_start:json_end].strip()
                # JSON geçerliliğini test et
                json.loads(json_data)
                logger.info(f"JSON bulundu (temizleme sonrası): {json_data[:100]}...")
                return json_data
            
            # Üçüncü deneme: Markdown code blocks
            if "```json" in text:
                start_marker = text.find("```json") + 7
                end_marker = text.find("```", start_marker)
                if end_marker != -1:
                    json_data = text[start_marker:end_marker].strip()
                    json.loads(json_data)  # Test
                    logger.info(f"JSON bulundu (markdown json): {json_data[:100]}...")
                    return json_data
            
            if "```" in text:
                start_marker = text.find("```") + 3
                end_marker = text.find("```", start_marker)
                if end_marker != -1:
                    json_data = text[start_marker:end_marker].strip()
                    json.loads(json_data)  # Test
                    logger.info(f"JSON bulundu (markdown): {json_data[:100]}...")
                    return json_data
            
            # Dördüncü deneme: Satır satır arama
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        json.loads(line)
                        logger.info(f"JSON bulundu (satır arama): {line[:100]}...")
                        return line
                    except:
                        continue
            
            logger.error(f"Hiçbir JSON bulunamadı. Tam metin: {text}")
            raise ValueError("Geçerli JSON bulunamadı")
            
        except Exception as e:
            logger.error(f"JSON çıkarma hatası: {e}")
            raise

    async def _parse_llm_response_manually(self, content: str) -> Dict[str, Any]:
        """LLM yanıtını manuel olarak parse eder"""
        try:
            # JSON çıkar
            json_data = self._extract_json_from_text(content)
            
            # Parse et
            parsed_result = json.loads(json_data)
            return parsed_result
                
        except Exception as e:
            logger.error(f"Manuel parse hatası: {e}")
            # En son çare: Sabit format
            return {
                "distortions": [
                    {
                        "type": "Genelleme",
                        "sentence": "Metin analiz edilemedi",
                        "explanation": "JSON parse hatası nedeniyle analiz yapılamadı",
                        "alternative": "Daha sonra tekrar deneyin",
                        "severity": "düşük",
                        "confidence": 0.1
                    }
                ],
                "risk_level": "belirsiz",
                "recommendations": ["Analiz sırasında teknik bir hata oluştu. Lütfen daha sonra tekrar deneyin."]
            }
    
    # Fallback analiz kaldırıldı - hız için
    
    async def _generate_suggestions_async(self, distortions: List[Dict]) -> List[str]:
        """Öneriler üretir"""
        try:
            if not distortions:
                return ["Herhangi bir bilişsel çarpıtma tespit edilmedi. Düşünceleriniz dengeli görünüyor."]
            
            suggestions = []
            for distortion in distortions:
                distortion_type = distortion.get("type", "")
                if distortion_type == "felaketleştirme":
                    suggestions.append("Gelecekte olacakları tahmin etmek yerine, şu anki duruma odaklanmayı deneyin.")
                elif distortion_type == "genelleme":
                    suggestions.append("Tek bir olaydan genel sonuçlar çıkarmak yerine, her durumu ayrı değerlendirin.")
                elif distortion_type == "zihin okuma":
                    suggestions.append("Başkalarının düşüncelerini tahmin etmek yerine, açık iletişim kurmayı deneyin.")
                elif distortion_type == "kişiselleştirme":
                    suggestions.append("Her şeyi kendinize mal etmek yerine, olayların farklı nedenleri olabileceğini düşünün.")
                else:
                    suggestions.append(f"'{distortion_type}' çarpıtması için: Daha dengeli ve gerçekçi bir bakış açısı geliştirmeye çalışın.")
            
            return suggestions
        except Exception as e:
            logger.error(f"Öneri üretme hatası: {e}")
            return ["Öneriler üretilirken hata oluştu."]
    
    def get_memory_summary(self) -> str:
        """Memory özetini döndürür"""
        return self.memory.buffer
    
    def clear_memory(self):
        """Memory'yi temizler"""
        self.memory.clear()