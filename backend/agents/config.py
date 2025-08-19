"""
Agent konfigürasyonu ve ayarları
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AgentConfig:
    """Agent konfigürasyon sınıfı"""
    
    # OpenAI ayarları
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    
    # Analiz ayarları
    MAX_DISTORTIONS_PER_ANALYSIS = int(os.getenv("MAX_DISTORTIONS", "5"))
    ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", "30"))
    
    # Memory ayarları
    MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "100"))
    MEMORY_TTL = int(os.getenv("MEMORY_TTL", "3600"))  # 1 saat
    
    # Risk değerlendirme ayarları
    HIGH_RISK_KEYWORDS = [
        "intihar", "ölmek", "yaşamak istemiyorum", "bitirmek",
        "kendimi öldürmek", "ölüm", "son", "bitiş"
    ]
    
    MEDIUM_RISK_KEYWORDS = [
        "umutsuz", "çaresiz", "değersiz", "yetersiz",
        "kimse beni sevmiyor", "herkes benden nefret ediyor"
    ]
    
    # Prompt şablonları
    SYSTEM_PROMPTS = {
        "cognitive_analysis": """Sen bir bilişsel davranışçı terapi (BDT) uzmanısın. 
        Kullanıcının günlük yazılarını analiz ederek bilişsel çarpıtmaları tespit etmek 
        ve alternatif düşünceler önermekle görevlisin.""",
        
        "risk_assessment": """Metindeki risk faktörlerini değerlendir ve 
        uygun risk seviyesini belirle.""",
        
        "suggestion_generation": """Tespit edilen çarpıtmalara göre 
        yapıcı ve destekleyici öneriler üret."""
    }
    
    # Çıktı formatları
    OUTPUT_FORMATS = {
        "analysis": {
            "distortions": "List[CognitiveDistortion]",
            "overall_mood": "str",
            "risk_level": "str",
            "recommendations": "List[str]",
            "analysis_timestamp": "str"
        }
    }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Konfigürasyon geçerliliğini kontrol eder"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY bulunamadı")
        
        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 1:
            raise ValueError("OPENAI_TEMPERATURE 0-1 arasında olmalı")
        
        return True
    
    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """Konfigürasyon özetini döndürür"""
        return {
            "openai_model": cls.OPENAI_MODEL,
            "openai_temperature": cls.OPENAI_TEMPERATURE,
            "max_distortions": cls.MAX_DISTORTIONS_PER_ANALYSIS,
            "analysis_timeout": cls.ANALYSIS_TIMEOUT,
            "memory_max_size": cls.MEMORY_MAX_SIZE,
            "risk_keywords_count": len(cls.HIGH_RISK_KEYWORDS) + len(cls.MEDIUM_RISK_KEYWORDS)
        }
