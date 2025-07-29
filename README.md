# 🪞 Mind Mirror

Zihin Aynası, kullanıcıların duygularını günlüğe kaydetmelerine ve yazılarına yapay zeka destekli bilişsel çarpıtma analizi yapılmasına olanak tanıyan tam yığın bir web uygulamasıdır.

---

## 🚀 Projeyi Başlatma

Bu proje iki ana bileşenden oluşur:

- **Backend:** FastAPI, PostgreSQL, Alembic, OpenAI entegrasyonu
- **Frontend:** React (Vite), Chakra UI

Aşağıdaki adımları takip ederek uygulamayı yerel ortamınızda çalıştırabilirsiniz.

---

## 🧠 Gereksinimler

### Ortak Gereksinimler

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
backend dizinine .env adlı bir dosya ekleyin ve aşağıdaki ortam değişkenlerini tanımlayın:

DATABASE_URL="postgresql://postgres:password@localhost/db_name"
OPENAI_API_KEY="your-openai-api-key-here"
JWT_SECRET_KEY="your-secret-key"

### 3.Veritabanı Migrasyonları (Alembic)
Veritabanı tablolarını oluşturmak için aşağıdaki komutu çalıştırın:

```bash
alembic upgrade head
```

4. Backend Uygulamasını Başlatma
```bash
uvicorn main:app --reload
```
Backend http://localhost:8000 adresinde çalışacaktır.

Frontend Kurulumu
### 1. Gerekli Paketleri Yükleme
```bash
cd frontend
npm install
```
### 2. Frontend Uygulamasını Başlatma
```bash
npm run dev
```
Frontend, varsayılan olarak http://localhost:5173 adresinde çalışır

