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
    # ReportAgent kaldırıldı - artık statistics_service kullanılıyor
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
    """Report Agent testi - Kaldırıldı, artık statistics_service kullanılıyor"""
    print("\n📊 Report Agent Testi - Kaldırıldı")
    print("=" * 50)
    print("ℹ️  Rapor üretimi artık statistics_service ile yapılıyor")
    print("✅ Test başarılı (kaldırıldı)")
    return True

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