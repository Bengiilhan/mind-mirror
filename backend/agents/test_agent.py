"""
Agent test dosyası - Basit testler için
"""

import asyncio
import os
import sys
from pathlib import Path

# Backend klasörünü Python path'ine ekle
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

# Test için gerekli importlar
try:
    from agents.cognitive_agent import CognitiveAnalysisAgent
    from agents.report_agent import ReportAgent
    from agents.factory import agent_factory
    print("✅ Tüm agent'lar başarıyla import edildi")
except ImportError as e:
    print(f"❌ Import hatası: {e}")

load_dotenv()

async def test_cognitive_agent():
    """Cognitive Analysis Agent'ı test eder"""
    print("\n🧠 Cognitive Analysis Agent Testi")
    print("=" * 50)
    
    try:
        # Agent oluştur
        agent = CognitiveAnalysisAgent()
        print("✅ Agent başarıyla oluşturuldu")
        
        # Test metni
        test_text = """
        Bugün işte çok kötü bir gün geçirdim. Patronum bana kızdı ve ben artık hiçbir işi doğru yapamayacağımı düşünüyorum. 
        Herkes benden nefret ediyor ve ben değersiz biriyim. Bu işi kaybedeceğim ve hiçbir yerde iş bulamayacağım.
        """
        
        print(f"📝 Test metni: {test_text[:100]}...")
        
        # Analiz yap
        result = await agent.analyze_entry(text=test_text, user_id="test_user")
        
        print("✅ Analiz tamamlandı")
        print(f"📊 Tespit edilen çarpıtma sayısı: {len(result.get('distortions', []))}")
        print(f"⚠️ Risk seviyesi: {result.get('risk_level', 'belirsiz')}")
        
        # Sonuçları göster
        for i, distortion in enumerate(result.get('distortions', []), 1):
            print(f"\n🔍 Çarpıtma {i}:")
            print(f"   Tür: {distortion.get('type', 'bilinmeyen')}")
            print(f"   Cümle: {distortion.get('sentence', '')[:80]}...")
            print(f"   Alternatif: {distortion.get('alternative', '')[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

async def test_report_agent():
    """Report Agent'ı test eder"""
    print("\n📊 Report Agent Testi")
    print("=" * 50)
    
    try:
        # Agent oluştur
        agent = ReportAgent()
        print("✅ Report Agent başarıyla oluşturuldu")
        
        # Test verileri
        test_entries = [
            {
                "distortions": [
                    {"type": "felaketleştirme", "sentence": "İşi kaybedeceğim"},
                    {"type": "genelleme", "sentence": "Hiçbir işi doğru yapamıyorum"}
                ],
                "mood_score": 3
            },
            {
                "distortions": [
                    {"type": "kişiselleştirme", "sentence": "Her şey benim hatam"}
                ],
                "mood_score": 4
            }
        ]
        
        print(f"📝 Test verisi: {len(test_entries)} günlük yazısı")
        
        # Haftalık rapor üret
        from datetime import datetime, timedelta
        week_start = datetime.now() - timedelta(days=7)
        
        report = await agent.generate_weekly_report(
            user_id="test_user",
            week_start=week_start,
            entries_data=test_entries
        )
        
        print("✅ Haftalık rapor üretildi")
        print(f"📊 Toplam yazı: {report.total_entries}")
        print(f"🔍 Toplam çarpıtma: {report.total_distortions}")
        print(f"📈 İlerleme puanı: {report.progress_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

async def test_factory():
    """Agent Factory'yi test eder"""
    print("\n🏭 Agent Factory Testi")
    print("=" * 50)
    
    try:
        print(f"📋 Mevcut agent türleri: {agent_factory.get_available_agents()}")
        
        # Cognitive agent oluştur
        cognitive_agent = agent_factory.create_agent("cognitive")
        print("✅ Cognitive agent factory ile oluşturuldu")
        
        # Agent durumunu kontrol et
        status = agent_factory.get_agent_status()
        print(f"📊 Agent durumları: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

async def main():
    """Ana test fonksiyonu"""
    print("🚀 Zihin Aynası Agent Testleri Başlıyor")
    print("=" * 60)
    
    # OpenAI API key kontrolü
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")
        return
    
    print("✅ OpenAI API key bulundu")
    
    # Testleri çalıştır
    tests = [
        test_factory,
        test_cognitive_agent,
        test_report_agent
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test çalıştırma hatası: {e}")
            results.append(False)
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("📋 TEST SONUÇLARI")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Başarılı: {passed}/{total}")
    print(f"❌ Başarısız: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 Tüm testler başarılı!")
    else:
        print("⚠️ Bazı testler başarısız. Lütfen hataları kontrol edin.")

if __name__ == "__main__":
    asyncio.run(main())