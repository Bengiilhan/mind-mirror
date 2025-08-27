# Agents - Zihin Aynası AI Agent Sistemi

Bu klasör, Zihin Aynası projesinin **LangChain tabanlı AI Agent sistemini** içerir. Agent'lar, bilişsel davranışçı terapi (BDT) prensiplerine dayalı otomatik analiz ve rapor üretimi yapar.

## 🏗️ Mimari Yapı

```
agents/
├── __init__.py              # Paket başlatıcı
├── cognitive_agent.py       # Ana analiz agent'ı
├── rag_agent.py             # Terapi teknikleri agent'ı
├── factory.py               # Agent factory pattern
├── config.py                # Konfigürasyon ayarları
├── test_agent.py            # Test dosyası
└── README.md                # Bu dosya
```

## 🤖 Agent Türleri

### 1. Cognitive Analysis Agent
**Dosya:** `cognitive_agent.py`

**Görev:** Kullanıcının günlük yazılarını analiz ederek bilişsel çarpıtmaları tespit eder.

**Özellikler:**
- GPT-4o-mini ile hızlı ve maliyet etkin analiz
- Pydantic modelleri ile structured output
- 10 farklı bilişsel çarpıtma türü tespiti
- Otomatik kriz tespiti ve acil hattı yönlendirmesi
- Çok aşamalı fallback sistemi
- ConversationBufferMemory ile geçmiş hatırlama

**Kullanım:**
```python
from agents.cognitive_agent import CognitiveAnalysisAgent

agent = CognitiveAnalysisAgent()
result = await agent.analyze_entry(text="Günlük yazısı", user_id="user123")
```

### 2. ChromaDB Destekli RAG Terapi Agent
**Dosya:** `rag_agent.py`

**Görev:** Bilişsel çarpıtma türlerine göre kişiselleştirilmiş terapi teknikleri önerir.

**Temel Özellikler:**
- **10 Çarpıtma Türü**: Felaketleştirme, zihin okuma, genelleme, kişiselleştirme, etiketleme, ya hep ya hiç, büyütme/küçültme, kehanetçilik, keyfi çıkarsama, meli/malı düşünceleri
- **30+ BDT Tekniği**: Her çarpıtma türü için 3-5 özel CBT tekniği
- **Zorluk Seviyeleri**: Kolay, orta, zor kategorilerinde teknikler
- **Pratik Egzersizler**: Uygulanabilir adım adım terapi egzersizleri
- **Kişiselleştirilmiş Öneriler**: Kullanıcı bağlamına göre uyarlanmış tavsiyeler
- **Sonraki Adımlar**: Kişisel gelişim için yol haritası ve takip sistemi

**ChromaDB Gelişmiş Özellikler:**
- **🔍 Semantik Arama**: ChromaDB vector database ile akıllı teknik eşleştirme
- **🧠 Hybrid RAG**: Vector database + statik BDT teknikleri kombinasyonu
- **👤 Geçmiş Tabanlı Kişiselleştirme**: Kullanıcının önceki deneyimlerine dayalı öneriler
- **📚 Vektörel Teknik Depolama**: 30 BDT tekniği ChromaDB'de embedding olarak saklı
- **🌍 Türkçe Embedding**: Multilingual sentence-transformers desteği
- **⚡ Gerçek Zamanlı İndeksleme**: Yeni girişlerin otomatik ChromaDB'ye eklenmesi
- **📊 Kullanıcı Kalıp Analizi**: Düşünce kalıpları ve eğilim tespiti
- **🔄 Fallback Sistemi**: ChromaDB başarısızlığında statik tekniklere dönüş

**Kullanım:**
```python
from agents.rag_agent import RAGAgent

therapy_agent = RAGAgent()
techniques = await therapy_agent.get_therapy_techniques(
    distortion_type="felaketleştirme",
    user_context="Kullanıcı yazısı",
    user_id="user123"  # Kişiselleştirme için
)
```

### 3. Statistics Service (Agent Dışında)
**Dosya:** `../services/statistics_service.py`

**Görev:** İstatistik hesaplama ve rapor üretimi.

**Özellikler:**
- Kullanıcı istatistikleri
- Mood analizi
- Çarpıtma istatistikleri
- AI içgörüleri
- Milestone sistemi

**Kullanım:**
```python
from services.statistics_service import StatisticsService

stats_service = StatisticsService()
stats = stats_service.get_user_statistics(db, user_id)
insights = await stats_service.generate_ai_insights(entry_texts, stats)
```

## 🏭 Factory Pattern

**Dosya:** `factory.py`

Agent'ları oluşturmak ve yönetmek için factory pattern kullanılır:

```python
from agents.factory import agent_factory

# Agent oluştur
cognitive_agent = agent_factory.create_agent("cognitive")

# Mevcut agent'ları listele
available_agents = agent_factory.get_available_agents()

# Agent durumunu kontrol et
status = agent_factory.get_agent_status()
```

## ⚙️ Konfigürasyon

**Dosya:** `config.py`

Tüm agent ayarları merkezi olarak yönetilir:

```python
from agents.config import AgentConfig

# Konfigürasyonu doğrula
AgentConfig.validate_config()

# Ayarları görüntüle
summary = AgentConfig.get_config_summary()
```

## 🧪 Test Etme

**Dosya:** `test_agent.py`

Agent'ları test etmek için:

```bash
cd mind-mirror/backend/agents
python test_agent.py
```

**Test Kapsamı:**
- Agent oluşturma
- Metin analizi
- Terapi teknikleri
- Rapor üretimi
- Factory pattern
- Hata yönetimi

## 🚀 Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
`.env` dosyasında:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
```

### 3. Test
```bash
python agents/test_agent.py
```

### 4. Not
Report Agent kaldırıldı. Rapor üretimi artık `statistics_service.py` ile yapılıyor.

## 📊 Performans

**Analiz Süresi:** 2-4 saniye (GPT-4o-mini ile)
**ChromaDB Terapi Teknik Süresi:** 1-3 saniye (semantik arama)
**Statik Teknik Süresi:** <1 saniye
**Başarı Oranı:** %95+
**Memory Kullanımı:** 65MB (ChromaDB dahil)
**API Çağrı Sayısı:** 1500/gün
**Model:** GPT-4o-mini + sentence-transformers
**ChromaDB:** 30 BDT tekniği vektörel olarak saklı
**Embedding Model:** paraphrase-multilingual-MiniLM-L12-v2

## 🔧 Hata Ayıklama

### Yaygın Sorunlar

**1. Import Hatası**
```bash
# Agents klasöründe olduğunuzdan emin olun
cd mind-mirror/backend/agents
python -c "from cognitive_agent import CognitiveAnalysisAgent"
```

**2. API Key Hatası**
```bash
# .env dosyasını kontrol edin
echo $OPENAI_API_KEY
```

**3. Memory Hatası**
```python
# Memory'yi temizleyin
agent.clear_memory()
```

## 🔮 Gelecek Geliştirmeler

- [ ] Real-time streaming analiz
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Integration APIs
- [x] Vector database support (ChromaDB ✅)
- [ ] Caching layer
- [ ] Daha gelişmiş embedding modelleri
- [ ] Multi-modal AI (ses, görüntü)

## 📝 API Endpoints

### Cognitive Analysis
- `POST /analyze/` - Tek metin analizi
- `POST /analyze/batch` - Toplu analiz
- `GET /analyze/memory/{user_id}` - Kullanıcı memory'si
- `DELETE /analyze/memory/{user_id}` - Memory temizleme
- `GET /analyze/health` - Sağlık kontrolü

### ChromaDB Destekli Terapi Teknikleri
- `POST /rag/techniques/` - Kişiselleştirilmiş terapi teknikleri (ChromaDB + AI)
- `POST /rag/techniques/multiple/` - Çoklu çarpıtma teknikleri
- `POST /rag/similar-entries/` - Benzer geçmiş deneyimler bulma
- `GET /rag/user-insights/` - Kullanıcı düşünce kalıpları analizi
- `GET /rag/chroma-stats/` - ChromaDB istatistikleri
- `POST /rag/techniques/semantic-search/` - Semantik teknik arama
- `GET /rag/distortions/` - Mevcut çarpıtma türleri
- `GET /rag/health/` - Sistem sağlık kontrolü (ChromaDB dahil)

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorun yaşıyorsanız:
1. Issues sekmesinde arama yapın
2. Yeni issue açın
3. Detaylı hata mesajı ve log'ları ekleyin

---

**Not:** Bu agent sistemi, LangChain 0.2.16, ChromaDB 0.4.24 ve sentence-transformers 2.2.2 sürümleri ile uyumludur. GPT-4o-mini modeli ile hız optimizasyonu, ChromaDB ile semantik arama ve kişiselleştirme özellikleri aktif edilmiştir.
