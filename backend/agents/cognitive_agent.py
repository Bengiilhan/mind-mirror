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
    overall_mood: str = Field(description="Genel ruh hali değerlendirmesi")
    risk_level: str = Field(description="Risk seviyesi (düşük/orta/yüksek)")
    recommendations: Optional[List[str]] = Field(default=[], description="Genel öneriler")
    analysis_timestamp: Optional[str] = Field(default=None, description="Analiz zamanı")

class CognitiveAnalysisAgent:
    """Bilişsel çarpıtma analizi için LangChain tabanlı agent"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Çıktı parser
        self.output_parser = JsonOutputParser(pydantic_object=AnalysisResult)
        
        # Sistem prompt'u
        self.system_prompt = """Sen bir bilişsel davranışçı terapi (BDT) uzmanısın. 
        Kullanıcının günlük yazılarını analiz ederek bilişsel çarpıtmaları tespit etmek 
        ve alternatif düşünceler önermekle görevlisin.

        Bilişsel çarpıtma türleri:
        - Felaketleştirme: En kötü senaryoları varsayma
        - Zihin okuma: Başkalarının düşüncelerini bildiğini varsayma
        - Genelleme: Tek olaydan genel sonuçlar çıkarma
        - Kişiselleştirme: Her şeyi kendine mal etme
        - Etiketleme: Kendini veya başkalarını etiketleme
        - Ya hep ya hiç: Siyah-beyaz düşünme
        - Büyütme/küçültme: Olumsuzları abartma, olumluları küçümseme
        - Kehanetçilik: Geleceği olumsuz tahmin etme
        - Keyfi çıkarsama: Kanıtsız sonuçlara varma
        - -meli/-malı düşünceleri: Katı kurallar koyma

        Analiz yaparken:
        1. Metni dikkatlice oku ve olumsuz düşünceleri tespit et
        2. Her çarpıtma için türünü belirle
        3. Şiddet seviyesini değerlendir
        4. Güvenilir alternatif düşünceler öner
        5. Genel ruh hali ve risk seviyesini değerlendir
        6. Yapıcı ve destekleyici bir ton kullan

        ÖNEMLİ: Eğer intihar düşüncesi veya ciddi kriz belirtileri tespit edersen,
        mutlaka profesyonel yardım öner ve risk seviyesini "yüksek" olarak işaretle.

                 YANIT FORMATI: Yanıtını kesinlikle aşağıdaki JSON formatında ver, başka hiçbir şey ekleme:
         {{
             "distortions": [
                 {{
                     "type": "çarpıtma_türü",
                     "sentence": "ilgili_cümle",
                     "explanation": "açıklama",
                     "alternative": "alternatif_düşünce",
                     "severity": "düşük/orta/yüksek",
                     "confidence": 0.8
                 }}
             ],
             "overall_mood": "genel_ruh_hali",
             "risk_level": "düşük/orta/yüksek",
             "recommendations": ["öneri1", "öneri2"]
         }}
        """
        
        # Ana analiz prompt'u - chat_history olmadan basit versiyon
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Lütfen aşağıdaki günlük yazısını analiz et:\n\n{text}")
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
            logger.info(f"Analiz başlatılıyor - Kullanıcı: {user_id}")
            
            # Risk değerlendirmesi
            risk_level = await self._assess_risk_async(text)
            
            # Ana analiz
            analysis_result = await self._analyze_text_async(text)
            
            # Debug: analysis_result tipini kontrol et
            logger.info(f"Analysis result type: {type(analysis_result)}")
            logger.info(f"Analysis result: {analysis_result}")
            
            # Öneriler üret
            if isinstance(analysis_result, dict):
                suggestions = await self._generate_suggestions_async(analysis_result.get("distortions", []))
            else:
                logger.error(f"Analysis result is not dict: {type(analysis_result)}")
                # Eğer dict değilse, fallback analiz kullan
                analysis_result = await self._fallback_analysis(text)
                suggestions = await self._generate_suggestions_async(analysis_result.get("distortions", []))
            
            # Sonuçları birleştir
            final_result = {
                **analysis_result,
                "risk_level": risk_level,
                "recommendations": suggestions,
                "analysis_timestamp": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Memory'ye kaydet
            self.memory.save_context(
                {"input": f"Analiz: {text[:100]}..."},
                {"output": json.dumps(final_result, ensure_ascii=False)}
            )
            
            logger.info(f"Analiz tamamlandı - {len(analysis_result.get('distortions', []))} çarpıtma tespit edildi")
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
    
    async def _assess_risk_async(self, text: str) -> str:
        """Risk değerlendirmesi yapar"""
        try:
            risk_prompt = f"""
            Aşağıdaki metni oku ve risk seviyesini değerlendir:
            - Düşük risk: Normal günlük yazısı
            - Orta risk: Depresif veya kaygılı düşünceler
            - Yüksek risk: İntihar düşüncesi, ciddi kriz belirtileri
            
            Metin: {text}
            
            Sadece risk seviyesini döndür: "düşük", "orta" veya "yüksek"
            """
            
            response = await self.llm.ainvoke(risk_prompt)
            return response.content.strip().lower()
        except:
            return "belirsiz"
    
    async def _analyze_text_async(self, text: str) -> Dict[str, Any]:
        """Metni analiz eder"""
        try:
            logger.info("🔍 LangChain chain ile analiz başlatılıyor...")
            
            # Önce prompt'u test edelim
            prompt_result = await self.analysis_prompt.ainvoke({"text": text})
            logger.info(f"📝 Prompt sonucu: {prompt_result}")
            
            # LLM'i test edelim
            llm_result = await self.llm.ainvoke(prompt_result)
            logger.info(f"🤖 LLM yanıtı: {llm_result.content}")
            
            # Output parser'ı test edelim
            try:
                parsed_result = await self.output_parser.ainvoke(llm_result.content)
                logger.info(f"✅ Output parser sonucu: {parsed_result}")
                
                # Parsed result'ın dict olduğundan emin ol
                if isinstance(parsed_result, dict):
                    return parsed_result
                else:
                    logger.error(f"❌ Output parser dict döndürmedi: {type(parsed_result)}")
                    # Fallback: Manuel JSON parse
                    return await self._parse_llm_response_manually(llm_result.content)
                    
            except Exception as parse_error:
                logger.error(f"❌ Output parser hatası: {parse_error}")
                # Fallback: Manuel JSON parse
                return await self._parse_llm_response_manually(llm_result.content)
            
        except Exception as e:
            logger.error(f"❌ LangChain analiz hatası: {e}")
            logger.info("🔄 Fallback analiz kullanılıyor...")
            # Fallback: Basit analiz
            return await self._fallback_analysis(text)
    
    def _extract_json_from_text(self, text: str) -> str:
        """Metinden JSON çıkarır"""
        try:
            # İlk deneme: Basit JSON arama
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            
            if json_start != -1 and json_end != 0:
                json_data = text[json_start:json_end].strip()
                # JSON geçerliliğini test et
                json.loads(json_data)
                return json_data
            
            # İkinci deneme: Temizleme
            cleaned_text = text.replace('\n', ' ').replace('\r', ' ').strip()
            json_start = cleaned_text.find("{")
            json_end = cleaned_text.rfind("}") + 1
            
            if json_start != -1 and json_end != 0:
                json_data = cleaned_text[json_start:json_end].strip()
                # JSON geçerliliğini test et
                json.loads(json_data)
                return json_data
            
            # Üçüncü deneme: Daha agresif temizleme
            # Markdown code blocks'ları kaldır
            if "```json" in text:
                start_marker = text.find("```json") + 7
                end_marker = text.find("```", start_marker)
                if end_marker != -1:
                    json_data = text[start_marker:end_marker].strip()
                    json.loads(json_data)  # Test
                    return json_data
            
            if "```" in text:
                start_marker = text.find("```") + 3
                end_marker = text.find("```", start_marker)
                if end_marker != -1:
                    json_data = text[start_marker:end_marker].strip()
                    json.loads(json_data)  # Test
                    return json_data
            
            raise ValueError("Geçerli JSON bulunamadı")
            
        except Exception as e:
            logger.error(f"JSON çıkarma hatası: {e}")
            raise

    async def _parse_llm_response_manually(self, content: str) -> Dict[str, Any]:
        """LLM yanıtını manuel olarak parse eder"""
        try:
            logger.info("🔧 Manuel JSON parse başlatılıyor...")
            logger.info(f"📝 Parse edilecek içerik: {content}")
            
            # JSON çıkar
            json_data = self._extract_json_from_text(content)
            logger.info(f"📋 Bulunan JSON: {json_data}")
            
            # Parse et
            parsed_result = json.loads(json_data)
            logger.info(f"✅ Manuel parse başarılı: {parsed_result}")
            return parsed_result
                
        except Exception as e:
            logger.error(f"❌ Manuel parse hatası: {e}")
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
                "overall_mood": "belirsiz",
                "risk_level": "belirsiz",
                "recommendations": ["Analiz sırasında teknik bir hata oluştu. Lütfen daha sonra tekrar deneyin."]
            }
    
    async def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback analiz - LLM hatası durumunda"""
        try:
            logger.info("🔄 Fallback analiz başlatılıyor...")
            
            # Basit prompt ile analiz
            simple_prompt = f"""
            Aşağıdaki metni analiz et ve bilişsel çarpıtmaları tespit et:
            
            Metin: {text}
            
            Yanıtı kesinlikle şu JSON formatında ver, başka hiçbir şey ekleme:
            {{
                "distortions": [
                    {{
                        "type": "çarpıtma_türü",
                        "sentence": "ilgili_cümle",
                        "explanation": "açıklama",
                        "alternative": "alternatif_düşünce",
                        "severity": "düşük/orta/yüksek",
                        "confidence": 0.7
                    }}
                ],
                "overall_mood": "genel_ruh_hali",
                "risk_level": "düşük/orta/yüksek",
                "recommendations": ["öneri1", "öneri2"]
            }}
            """
            
            response = await self.llm.ainvoke(simple_prompt)
            content = response.content.strip()
            logger.info(f"📝 Fallback LLM yanıtı: {content}")
            
            # JSON çıkar
            json_data = self._extract_json_from_text(content)
            parsed_result = json.loads(json_data)
            logger.info(f"✅ Fallback JSON parse başarılı: {parsed_result}")
            return parsed_result
                
        except Exception as e:
            logger.error(f"❌ Fallback analiz hatası: {e}")
            # En son çare: Sabit format
            return {
                "distortions": [
                    {
                        "type": "Genelleme",
                        "sentence": text[:100] + "..." if len(text) > 100 else text,
                        "explanation": "Metin analiz edilemedi, genel bir değerlendirme yapıldı",
                        "alternative": "Daha detaylı analiz için tekrar deneyin",
                        "severity": "düşük",
                        "confidence": 0.1
                    }
                ],
                "overall_mood": "belirsiz",
                "risk_level": "belirsiz",
                "recommendations": ["Analiz sırasında teknik bir hata oluştu. Lütfen daha sonra tekrar deneyin."]
            }
    
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