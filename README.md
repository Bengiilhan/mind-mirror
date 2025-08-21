# 🪞 Mind Mirror

Zihin Aynası, kullanıcıların duygularını günlüğe kaydetmelerine ve yazılarına **yapay zeka destekli bilişsel çarpıtma analizi** yapılmasına olanak tanıyan tam yığın bir web uygulamasıdır. Proje, **LangChain tabanlı AI agent sistemi** ile gelişmiş analiz ve otomasyon özellikleri sunar.

## ✨ Özellikler

### 🧠 AI Destekli Analiz
- **Bilişsel Çarpıtma Tespiti**: GPT-4o-mini ile otomatik bilişsel çarpıtma analizi
- **Risk Değerlendirmesi**: Yüksek risk durumlarında otomatik kriz uyarı sistemi
- **Alternatif Düşünce Önerileri**: Kişiselleştirilmiş düşünce alternatifleri
- **Structured Output**: Pydantic modelleri ile güvenilir JSON çıktısı
- **Fallback Sistemi**: Çok aşamalı hata yönetimi ve JSON çıkarma

### 📊 Gelişmiş İstatistikler
- **Mood Takibi**: Duygu durumu trend analizi ve grafikleri
- **Çarpıtma İstatistikleri**: En yaygın bilişsel çarpıtmaların analizi
- **İlerleme Takibi**: Milestone sistemi ve otomatik istatistik güncellemeleri
- **AI İçgörüleri**: Yapay zeka destekli kişisel gelişim önerileri

### 🤖 Otomasyon Sistemi
- **Otomatik Analiz**: Günlük yazıların anında analizi
- **Akıllı İstatistikler**: Otomatik istatistik hesaplama ve raporlama
- **Risk Tespiti**: Güvenlik odaklı otomatik kontrol
- **Factory Pattern**: Modüler agent yönetimi

### 🎨 Modern Kullanıcı Arayüzü
- **Responsive Tasarım**: Tüm cihazlarda mükemmel görünüm
- **Dark/Light Mode**: Kullanıcı tercihine göre tema
- **Gerçek Zamanlı Grafikler**: İnteraktif istatistik görselleştirmeleri
- **Toast Bildirimleri**: Kullanıcı dostu geri bildirimler

---

## 🏗️ Proje Yapısı

```
mind-mirror/
├── backend/
│   ├── agents/                 # 🤖 AI Agent Sistemi
│   │   ├── cognitive_agent.py  # Ana analiz agent'ı
│   │   ├── factory.py          # Agent factory pattern
│   │   ├── config.py           # Konfigürasyon ayarları
│   │   └── automation.md       # Otomasyon dokümantasyonu
│   ├── routers/
│   │   └── statistics.py       # İstatistik API'leri
│   ├── services/
│   │   └── statistics_service.py # İstatistik ve rapor servisleri
│   ├── models.py               # Veritabanı modelleri
│   ├── schemas.py              # Pydantic şemaları
│   └── main.py                 # FastAPI uygulaması
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Stats/          # 📊 İstatistik bileşenleri
│   │   │   │   ├── MoodChart.jsx
│   │   │   │   └── DistortionChart.jsx
│   │   │   ├── Statistics.jsx  # Ana istatistik sayfası
│   │   │   └── UI/             # UI bileşenleri
│   │   └── pages/              # Sayfa bileşenleri
│   └── package.json
└── README.md
```

---

## 🚀 Projeyi Başlatma

Bu proje iki ana bileşenden oluşur:

- **Backend:** FastAPI, PostgreSQL, Alembic, OpenAI + LangChain entegrasyonu
- **Frontend:** React (Vite), Modern UI bileşenleri

### 🧠 Gereksinimler

- Python 3.10+
- Node.js (18.x veya üzeri)
- PostgreSQL veritabanı
- OpenAI API Key

---

## ⚙️ Backend Kurulumu

### 1. Sanal Ortam Oluşturma ve Bağımlılıkları Yükleme

```bash
cd backend
python -m venv venv
venv\\Scripts\\activate    # Linux/macOS için: source venv/bin/activate
pip install -r requirements.txt
```

### 2. .env Dosyası Oluşturma

DATABASE_URL="postgresql://postgres:password@localhost/db_name"
OPENAI_API_KEY="your-openai-api-key-here"
JWT_SECRET_KEY="your-secret-key"
OPENAI_MODEL="gpt-4o-mini"
OPENAI_TEMPERATURE="0.0"

### 3. Veritabanı Migrasyonları

```bash
alembic upgrade head
```

### 4. Backend Uygulamasını Başlatma

```bash
uvicorn main:app --reload
```

Backend http://localhost:8000 adresinde çalışacaktır.

---

## 🎨 Frontend Kurulumu

### 1. Gerekli Paketleri Yükleme

```bash
cd frontend
npm install
```

### 2. Frontend Uygulamasını Başlatma

```bash
npm run dev
```

Frontend, varsayılan olarak http://localhost:5173 adresinde çalışır.

---

## 🤖 AI Agent Sistemi

### Cognitive Analysis Agent

Ana analiz agent'ı, kullanıcı yazılarını analiz ederek bilişsel çarpıtmaları tespit eder:

```python
from agents.cognitive_agent import CognitiveAnalysisAgent

agent = CognitiveAnalysisAgent()
result = await agent.analyze_entry(
    text="Günlük yazısı", 
    user_id="user123"
)
```

**Özellikler:**
- **Structured Output**: Pydantic modelleri ile güvenilir JSON çıktısı
- **Risk Değerlendirmesi**: Otomatik kriz tespiti ve Türkiye acil hattı yönlendirmesi
- **Fallback Sistemi**: Çok aşamalı hata yönetimi ve JSON çıkarma
- **Çarpıtma Tespiti**: 10 farklı bilişsel çarpıtma türü
- **Alternatif Düşünce**: Kişiselleştirilmiş öneriler
- **Memory Sistemi**: ConversationBufferMemory ile geçmiş hatırlama

### Statistics Service

İstatistik ve rapor üretimi için gelişmiş servis:

```python
from services.statistics_service import StatisticsService

stats_service = StatisticsService()
stats = stats_service.get_user_statistics(db, user_id)
insights = await stats_service.generate_ai_insights(entry_texts, stats)
```

### Factory Pattern

Agent'ları yönetmek için factory pattern kullanılır:

```python
from agents.factory import agent_factory

# Agent oluştur
cognitive_agent = agent_factory.create_agent("cognitive")

# Mevcut agent'ları listele
available_agents = agent_factory.get_available_agents()
```

---

## 📊 İstatistik Sistemi

### API Endpoints

- `GET /statistics/` - Kullanıcı istatistikleri
- `GET /statistics/should-generate` - İstatistik oluşturma kontrolü
- `GET /statistics/insights` - AI içgörüleri
- `GET /statistics/progress` - İlerleme özeti

### Özellikler

- **Mood Analizi**: Duygu durumu trendleri
- **Çarpıtma İstatistikleri**: En yaygın bilişsel çarpıtmalar
- **Risk Analizi**: Yüksek risk yüzdeleri
- **İlerleme Takibi**: Milestone sistemi

---

## 🔧 API Endpoints

### Kimlik Doğrulama
- `POST /register` - Kullanıcı kaydı
- `POST /login` - Giriş yapma
- `GET /me` - Kullanıcı bilgileri

### Günlük Yazıları
- `POST /entries/` - Yeni yazı oluşturma (otomatik analiz ile)
- `GET /entries/` - Yazıları listeleme
- `PUT /entries/{id}` - Yazı güncelleme
- `DELETE /entries/{id}` - Yazı silme

### AI Analiz
- `POST /analyze/` - Tek metin analizi
- `POST /analyze/batch` - Toplu analiz
- `GET /analyze/memory/{user_id}` - Kullanıcı memory'si
- `DELETE /analyze/memory/{user_id}` - Memory temizleme

### İstatistikler
- `GET /statistics/` - Kullanıcı istatistikleri
- `GET /statistics/insights` - AI içgörüleri
- `GET /statistics/progress` - İlerleme özeti

---

## 🧪 Test Etme

### Agent Testleri

```bash
cd mind-mirror/backend/agents
python test_agent.py
```

### Backend Testleri

```bash
cd mind-mirror/backend
python -m pytest test_*.py
```

---

## 🔮 Gelecek Geliştirmeler

- [ ] Real-time streaming analiz
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration APIs
- [ ] Vector database support
- [ ] Caching layer
- [ ] Mobile app development

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 🆘 Destek

Sorun yaşıyorsanız:
1. Issues sekmesinde arama yapın
2. Yeni issue açın
3. Detaylı hata mesajı ve log'ları ekleyin

---

**Not:** Bu proje LangChain 0.2.16 sürümü ile uyumludur. GPT-4o-mini modeli kullanılarak hız ve maliyet optimizasyonu sağlanmıştır. Structured output ve fallback sistemi ile güvenilir analiz sonuçları garanti edilir.

