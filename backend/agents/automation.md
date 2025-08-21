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

**Risk Tespiti:**
```python
# Yüksek risk durumunda otomatik kriz önerisi
if (result.risk_level or "").lower() == "yüksek":
    crisis_tip = (
        "Kriz belirtileri tespit edildi. Lütfen en yakın acil hattı ile iletişime geçin ve "
        "güvendiğiniz birine haber verin. Türkiye için 112 Acil."
    )
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
from langchain_core.pydantic_v1 import BaseModel, Field

llm = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=0.0,
    model_kwargs={"response_format": {"type": "json_object"}}
)
structured_llm = llm.with_structured_output(AnalysisResult)
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

# Memory yönetimi
agent.get_memory_summary()  # Memory özetini al
agent.clear_memory()        # Memory'yi temizle
```

### 4.3 Çıktı Formatları

**Bilişsel Çarpıtma Modeli:**
```python
class CognitiveDistortion(BaseModel):
    type: str = Field(description="Çarpıtma türü (örn: felaketleştirme, zihin okuma, genelleme)")
    sentence: str = Field(description="Çarpıtma içeren cümle")
    explanation: str = Field(description="Neden bu çarpıtma olduğuna dair açıklama")
    alternative: str = Field(description="Daha sağlıklı alternatif düşünce")
    severity: Optional[str] = Field(default="orta", description="Çarpıtmanın şiddeti (düşük/orta/yüksek)")
    confidence: Optional[float] = Field(default=0.7, description="Tespit güvenilirliği (0-1 arası)")
```

**Analiz Sonucu:**
```python
class AnalysisResult(BaseModel):
    distortions: List[CognitiveDistortion] = Field(default_factory=list, description="Tespit edilen bilişsel çarpıtmalar")
    risk_level: str = Field(description="Risk seviyesi (düşük/orta/yüksek)")
    recommendations: List[str] = Field(default_factory=list, description="Genel öneriler")
    analysis_timestamp: Optional[str] = Field(default=None, description="Analiz zamanı")
```

## 5. Konfigürasyon

### 5.1 Environment Variables

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
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

