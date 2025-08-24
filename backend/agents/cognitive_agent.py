"""
Cognitive Analysis Agent - Bilişsel Çarpıtma Tespiti için LangChain Agent
Bu agent, kullanıcının günlük yazılarını analiz ederek bilişsel çarpıtmaları tespit eder
ve alternatif düşünceler üretir.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.memory import ConversationBufferMemory

# -----------------------------------------------------------------------------
# Logging konfigürasyonu
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Pydantic Modelleri
# -----------------------------------------------------------------------------
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
    distortions: List[CognitiveDistortion] = Field(default_factory=list, description="Tespit edilen bilişsel çarpıtmalar")
    risk_level: str = Field(description="Risk seviyesi (düşük/orta/yüksek)")
    recommendations: List[str] = Field(default_factory=list, description="Genel öneriler")
    analysis_timestamp: Optional[str] = Field(default=None, description="Analiz zamanı")

# -----------------------------------------------------------------------------
# Sistem Promptu
# -----------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "BDT uzmanı olarak günlük yazısını analiz et ve SADECE JSON üret.\n"
    "Çarpıtma türleri: Felaketleştirme, Zihin okuma, Genelleme, Kişiselleştirme, Etiketleme, "
    "Ya hep ya hiç, Büyütme/küçültme, Kehanetçilik, Keyfi çıkarsama, -meli/-malı düşünceleri.\n\n"
    "Kurallar:\n"
    "- Doğrudan kullanıcıya hitap et (sen/siz).\n"
    "- İntihar, kendine zarar veya başkalarına zarar düşüncesi varsa risk_level=\"yüksek\".\n"
    "- Sadece istenen JSON alanlarını üret.\n\n"
    "Şema:\n"
    "{\n"
    "  \"distortions\": [\n"
    "    {\n"
    "      \"type\": \"çarpıtma_türü\",\n"
    "      \"sentence\": \"ilgili_cümle\",\n"
    "      \"explanation\": \"Bu düşünce şu nedenle çarpıtmadır...\",\n"
    "      \"alternative\": \"alternatif_düşünce\",\n"
    "      \"severity\": \"düşük/orta/yüksek\",\n"
    "      \"confidence\": 0.8\n"
    "    }\n"
    "  ],\n"
    "  \"risk_level\": \"düşük/orta/yüksek\",\n"
    "  \"recommendations\": [\"öneri1\", \"öneri2\"]\n"
    "}\n"
)

# -----------------------------------------------------------------------------
# Agent Sınıfı
# -----------------------------------------------------------------------------
class CognitiveAnalysisAgent:
    """Bilişsel çarpıtma analizi için LangChain tabanlı agent"""

    def __init__(self) -> None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Hız/maliyet/kalite dengesi
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            logger.warning("OPENAI_API_KEY bulunamadı. Lütfen ortam değişkenini ayarlayın.")

        # JSON çıktısını zorlamak için OpenAI JSON mode kullanımı
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0.0,
            max_tokens=1000,  # Daha kısa çıktı için azaltıldı
            timeout=60,        # Timeout artırıldı
            max_retries=3,     # Retry sayısı artırıldı
            model_kwargs={"response_format": {"type": "json_object"}},
        )

        # Metin çıktısı için ayrı LLM (JSON formatı zorunluluğu olmadan)
        self.text_llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=0.7,  # Daha yaratıcı metinler için biraz artırıldı
            max_tokens=1000,
            timeout=60,
            max_retries=3,
        )

        # Yapısal çıktı (Pydantic) — AnalysisResult şemasına map eder
        self.structured_llm = self.llm.with_structured_output(AnalysisResult)

        # Prompt
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Analiz et:\n{text}"),
        ])

        # Memory (gerekiyorsa sonradan kullanılabilir)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
        )

        # Basit analiz için konfigürasyon (gelecek genişletmeler için placeholder)
        self._setup_simple_analysis()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def analyze_entry(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Günlük yazısını analiz eder ve yapılandırılmış sonuç döndürür."""
        try:
            # 1) Yapısal çıktı ile birincil deneme
            chain = self.analysis_prompt | self.structured_llm
            result: AnalysisResult = await chain.ainvoke({"text": text})

            # 2) Önerileri zenginleştir (boşsa veya azsa)
            recs = list(result.recommendations or [])
            if not recs:
                # distortions'a dayalı minimal öneriler ekle
                recs = await self._generate_suggestions_async([d.dict() for d in result.distortions])

            # 3) Yüksek risk durumunda kısa kriz önerisi ekle (TR bağlam)
            if (result.risk_level or "").lower() == "yüksek":
                crisis_tip = (
                    "Kriz belirtileri tespit edildi. Lütfen en yakın acil hattı ile iletişime geçin ve "
                    "güvendiğiniz birine haber verin. Türkiye için 112 Acil."
                )
                if crisis_tip not in recs:
                    recs.insert(0, crisis_tip)

            # 4) Zaman damgası ve user_id ile zenginleştir
            payload = result.dict()
            payload["recommendations"] = recs
            payload["analysis_timestamp"] = datetime.now().isoformat()
            if user_id is not None:
                payload["user_id"] = user_id

            # Memory'ye kayıt (isteğe bağlı — performans için kapalı bırakılabilir)
            # self.memory.save_context({"input": text[:200]}, {"output": json.dumps(payload, ensure_ascii=False)})

            return payload

        except Exception as e:
            logger.exception("Analiz hatası")
            # 5) Fallback: Serbest metin yanıtını JSON'a dönüştürmeye çalışma (ek güvenlik)
            try:
                raw = await self._analyze_text_async(text)
                raw["analysis_timestamp"] = datetime.now().isoformat()
                if user_id is not None:
                    raw["user_id"] = user_id
                return raw
            except Exception:
                pass

            # 6) Minimum geçerli şema ile geri dön
            return {
                "distortions": [],
                "risk_level": "belirsiz",
                "recommendations": ["Analiz sırasında teknik bir hata oluştu, lütfen tekrar deneyin."],
                "analysis_timestamp": datetime.now().isoformat(),
                **({"user_id": user_id} if user_id is not None else {}),
            }

    def get_memory_summary(self) -> str:
        """Memory özetini döndürür (şu an ham buffer)."""
        return self.memory.buffer

    def clear_memory(self) -> None:
        """Memory'yi temizler."""
        self.memory.clear()

    # ------------------------------------------------------------------
    # İç Yardımcılar
    # ------------------------------------------------------------------
    def _setup_simple_analysis(self) -> None:
        """Basit analiz için gerekli ayarlar (gelecek kullanım için placeholder)."""
        return

    async def _analyze_text_async(self, text: str) -> Dict[str, Any]:
        """Yapısal çağrı başarısız olursa: JSON modda tek atış fallback."""
        prompt = (
            "BDT uzmanı. Günlük yazısını analiz et. Çarpıtmaları tespit et.\n\n"
            "Çarpıtma türleri: Felaketleştirme, Zihin okuma, Genelleme, Kişiselleştirme, Etiketleme, "
            "Ya hep ya hiç, Büyütme/küçültme, Kehanetçilik, Keyfi çıkarsama, -meli/-malı düşünceleri.\n\n"
            "KURALLAR: Doğrudan kullanıcıya hitap et (sen, siz). İntihar düşüncesi varsa risk=\"yüksek\" yap.\n\n"
            f"Metin: {text}\n\n"
            "SADECE JSON formatında yanıt ver, başka hiçbir şey ekleme:\n"
            "{\n"
            "    \"distortions\": [\n"
            "        {\n"
            "            \"type\": \"çarpıtma_türü\",\n"
            "            \"sentence\": \"ilgili_cümle\",\n"
            "            \"explanation\": \"Bu düşünce şu nedenle çarpıtmadır...\",\n"
            "            \"alternative\": \"alternatif_düşünce\",\n"
            "            \"severity\": \"düşük/orta/yüksek\",\n"
            "            \"confidence\": 0.8\n"
            "        }\n"
            "    ],\n"
            "    \"risk_level\": \"düşük/orta/yüksek\",\n"
            "    \"recommendations\": [\"öneri1\", \"öneri2\"]\n"
            "}"
        )

        response = await self.llm.ainvoke(prompt)

        # JSON parse
        try:
            return json.loads(response.content)
        except Exception:
            json_text = self._extract_json_from_text(response.content)
            return json.loads(json_text)

    def _extract_json_from_text(self, text: str) -> str:
        """Metinden JSON çıkarır (çok aşamalı)."""
        try:
            # Basit aralık
            s = text.find("{")
            e = text.rfind("}") + 1
            if s != -1 and e > s:
                candidate = text[s:e].strip()
                json.loads(candidate)
                return candidate

            # Temizlenmiş metin
            cleaned = text.replace("\n", " ").replace("\r", " ").strip()
            s = cleaned.find("{")
            e = cleaned.rfind("}") + 1
            if s != -1 and e > s:
                candidate = cleaned[s:e].strip()
                json.loads(candidate)
                return candidate

            # Markdown blokları
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end != -1:
                    candidate = text[start:end].strip()
                    json.loads(candidate)
                    return candidate

            if "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                if end != -1:
                    candidate = text[start:end].strip()
                    json.loads(candidate)
                    return candidate

            # Satır satır
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        json.loads(line)
                        return line
                    except Exception:
                        continue

            raise ValueError("Geçerli JSON bulunamadı")
        except Exception as e:
            logger.error(f"JSON çıkarma hatası: {e}")
            raise

    async def _generate_suggestions_async(self, distortions: List[Dict[str, Any]]) -> List[str]:
        """Çarpıtma tiplerine dayalı basit öneriler üretir."""
        try:
            if not distortions:
                return [
                    "Herhangi bir bilişsel çarpıtma tespit edilmedi. Düşünceleriniz dengeli görünüyor."
                ]

            tips: List[str] = []
            for d in distortions:
                t = (d.get("type") or "").strip().lower()
                if "felaket" in t:
                    tips.append("Geleceği tahmin etmek yerine, şu ana odaklanmayı deneyin.")
                elif "genelle" in t:
                    tips.append("Tek bir olaydan genel sonuçlar çıkarmak yerine, her durumu ayrı değerlendirin.")
                elif "zihin okuma" in t:
                    tips.append("Başkalarının düşüncelerini tahmin etmek yerine, açık iletişim kurmayı deneyin.")
                elif "kişiselle" in t:
                    tips.append("Her şeyi kendinize mal etmek yerine, olayların farklı nedenleri olabileceğini düşünün.")
                else:
                    tips.append(
                        f"'{d.get('type', 'bilinmeyen')}' için: Daha dengeli ve gerçekçi bir bakış açısı geliştirmeye çalışın."
                    )

            # tekrarları sil (sıra korunur)
            seen = set()
            uniq = []
            for t in tips:
                if t not in seen:
                    seen.add(t)
                    uniq.append(t)
            return uniq
        except Exception as e:
            logger.error(f"Öneri üretme hatası: {e}")
            return ["Öneriler üretilirken hata oluştu."]
