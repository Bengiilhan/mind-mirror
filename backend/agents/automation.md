# Zihin Aynası - Otomasyon ve Agent Mimarisi Dokümantasyonu

## 1. Genel Bakış

Bu dokümantasyon, Zihin Aynası projesinde uygulanan **LangChain Agent Mimarisi** ve **Otomasyon Sistemi**'ni açıklar. Sistem, bilişsel çarpıtma tespiti ve analizi için gelişmiş AI agent'ları kullanır.

## 2. Agent Mimarisi

### 2.1 Ana Bileşenler

#### CognitiveAnalysisAgent
- **Görev**: Günlük yazılarında bilişsel çarpıtmaları tespit eder
- **Özellikler**:
  - Çok aşamalı analiz (DoT - Diagnosis of Thought)
  - Risk değerlendirmesi
  - Alternatif düşünce üretimi
  - Memory sistemi ile kullanıcı geçmişi

#### ReportAgent
- **Görev**: Haftalık ve aylık analiz raporları üretir
- **Özellikler**:
  - İstatistiksel analiz
  - İlerleme takibi
  - Kişiselleştirilmiş öneriler
  - Trend analizi

### 2.2 Agent Factory Pattern

```python
from agents.factory import agent_factory

# Agent oluştur
cognitive_agent = agent_factory.create_agent("cognitive")

# Mevcut agent'ı al
existing_agent = agent_factory.get_agent("cognitive")
```

## 3. Otomasyon Senaryoları

### 3.1 Günlük Yazı Analiz Otomasyonu

**Akış:**
1. Kullanıcı günlük yazısını gönderir
2. CognitiveAnalysisAgent otomatik olarak tetiklenir
3. Çok aşamalı analiz yapılır:
   - Risk değerlendirmesi
   - Bilişsel çarpıtma tespiti
   - Alternatif düşünce üretimi
4. Sonuçlar veritabanına kaydedilir
5. Kullanıcıya yapılandırılmış yanıt döner

**Kod Örneği:**
```python
@router.post("/")
async def analyze_entry(request: AnalysisRequest):
    result = await cognitive_agent.analyze_entry(
        text=request.text,
        user_id=request.user_id
    )
    return result
```

### 3.2 Haftalık Rapor Üretim Otomasyonu

**Akış:**
1. Her hafta sonu otomatik tetiklenir
2. Kullanıcının haftalık verileri toplanır
3. ReportAgent ile analiz yapılır
4. İstatistiksel grafikler oluşturulur
5. Kişiselleştirilmiş öneriler üretilir

**Kod Örneği:**
```python
async def generate_weekly_report(user_id: str, week_start: datetime, entries_data: List[Dict]):
    stats = agent._analyze_weekly_data(entries_data)
    report = await agent._generate_report_with_llm(...)
    return WeeklyReport(**report)
```

### 3.3 Risk Tespit ve Güvenlik Otomasyonu

**Akış:**
1. Her metin analizinde risk değerlendirmesi yapılır
2. Yüksek risk tespit edilirse:
   - Otomatik profesyonel yardım yönlendirmesi
   - Acil durum bildirimleri
   - Risk seviyesi yükseltilir

**Risk Anahtar Kelimeleri:**
```python
HIGH_RISK_KEYWORDS = [
    "intihar", "ölmek", "yaşamak istemiyorum", "bitirmek",
    "kendimi öldürmek", "ölüm", "son", "bitiş"
]
```

## 4. Teknik Detaylar

### 4.1 LangChain Entegrasyonu

**Kurulum:**
```bash
pip install langchain langchain-openai langchain-community langchain-core
```

**Temel Kullanım:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(model="gpt-4", temperature=0.3)
prompt = ChatPromptTemplate.from_messages([...])
parser = JsonOutputParser()
```

### 4.2 Memory Sistemi

**ConversationBufferMemory:**
- Kullanıcı analiz geçmişini saklar
- Tutarlı öneriler üretir
- Context awareness sağlar

**Kullanım:**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
```

### 4.3 Çıktı Formatları

**Bilişsel Çarpıtma Modeli:**
```python
class CognitiveDistortion(BaseModel):
    type: str                    # Çarpıtma türü
    sentence: str                # İlgili cümle
    explanation: str             # Açıklama
    alternative: str             # Alternatif düşünce
    severity: str                # Şiddet seviyesi
    confidence: float            # Güvenilirlik (0-1)
```

**Analiz Sonucu:**
```python
class AnalysisResult(BaseModel):
    distortions: List[CognitiveDistortion]
    overall_mood: str
    risk_level: str
    recommendations: List[str]
    analysis_timestamp: str
```

## 5. Konfigürasyon

### 5.1 Environment Variables

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
OPENAI_MAX_TOKENS=2000
MAX_DISTORTIONS=5
ANALYSIS_TIMEOUT=30
MEMORY_MAX_SIZE=100
MEMORY_TTL=3600
```

### 5.2 Agent Konfigürasyonu

```python
from agents.config import AgentConfig

# Konfigürasyonu doğrula
AgentConfig.validate_config()

# Konfigürasyon özetini al
config_summary = AgentConfig.get_config_summary()
```

