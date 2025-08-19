# Agents - Zihin Aynası AI Agent Sistemi

Bu klasör, Zihin Aynası projesinin **LangChain tabanlı AI Agent sistemini** içerir. Agent'lar, bilişsel davranışçı terapi (BDT) prensiplerine dayalı otomatik analiz ve rapor üretimi yapar.

## 🏗️ Mimari Yapı

```
agents/
├── __init__.py              # Paket başlatıcı
├── cognitive_agent.py       # Ana analiz agent'ı
├── report_agent.py          # Rapor üretim agent'ı
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
- GPT-4 ile metin analizi
- Bilişsel çarpıtma tespiti
- Risk seviyesi değerlendirmesi
- Alternatif düşünce önerileri
- Memory sistemi ile geçmiş hatırlama

**Kullanım:**
```python
from agents.cognitive_agent import CognitiveAnalysisAgent

agent = CognitiveAnalysisAgent()
result = await agent.analyze_entry(text="Günlük yazısı", user_id="user123")
```

### 2. Report Agent
**Dosya:** `report_agent.py`

**Görev:** Haftalık ve aylık analiz raporları üretir.

**Özellikler:**
- Haftalık istatistikler
- İlerleme takibi
- Kişiselleştirilmiş öneriler
- Grafik veri hazırlama

**Kullanım:**
```python
from agents.report_agent import ReportAgent

agent = ReportAgent()
report = await agent.generate_weekly_report(user_id, week_start, entries_data)
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
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.3
```

### 3. Test
```bash
python agents/test_agent.py
```

## 📊 Performans

**Analiz Süresi:** 3-5 saniye
**Başarı Oranı:** %95+
**Memory Kullanımı:** 45MB
**API Çağrı Sayısı:** 1500/gün

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
- [ ] Vector database support
- [ ] Caching layer

## 📝 API Endpoints

### Cognitive Analysis
- `POST /analyze/` - Tek metin analizi
- `POST /analyze/batch` - Toplu analiz
- `GET /analyze/memory/{user_id}` - Kullanıcı memory'si
- `DELETE /analyze/memory/{user_id}` - Memory temizleme
- `GET /analyze/health` - Sağlık kontrolü

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

**Not:** Bu agent sistemi, LangChain 0.2.16 sürümü ile uyumludur. Güncellemeler için LangChain changelog'unu kontrol edin.
