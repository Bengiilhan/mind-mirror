#!/usr/bin/env python3
"""
Backend Test Script
"""

import asyncio
import sys
import os

# Backend klasörünü Python path'ine ekle
sys.path.insert(0, os.path.dirname(__file__))

async def test_agent():
    """Agent'ı test eder"""
    try:
        from agents.cognitive_agent import CognitiveAnalysisAgent
        
        print("🧠 Agent test ediliyor...")
        
        # Agent instance oluştur
        agent = CognitiveAnalysisAgent()
        
        # Test metni
        test_text = "Bugün çok kötü bir gün. Hiçbir şey yolunda gitmiyor. Herkes benden nefret ediyor."
        
        print(f"📝 Test metni: {test_text}")
        
        # Analiz yap
        result = await agent.analyze_entry(
            text=test_text,
            user_id="test_user"
        )
        
        print("✅ Analiz sonucu:")
        print(f"   - Çarpıtma sayısı: {len(result.get('distortions', []))}")
        print(f"   - Risk seviyesi: {result.get('risk_level', 'N/A')}")
        print(f"   - Genel mood: {result.get('overall_mood', 'N/A')}")
        
        if result.get('distortions'):
            print("   - Çarpıtmalar:")
            for i, d in enumerate(result['distortions']):
                print(f"     {i+1}. {d.get('type', 'N/A')}: {d.get('sentence', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_analyze_endpoint():
    """Analyze endpoint'ini test eder"""
    try:
        from analyze import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        print("🔍 Analyze endpoint test ediliyor...")
        
        # Test app oluştur
        app = FastAPI()
        app.include_router(router, prefix="/analyze")
        
        client = TestClient(app)
        
        # Test request
        test_data = {
            "text": "Bugün çok kötü bir gün. Hiçbir şey yolunda gitmiyor.",
            "user_id": "test_user"
        }
        
        response = client.post("/analyze/", json=test_data)
        
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Endpoint test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Ana test fonksiyonu"""
    print("🚀 Backend Test Başlıyor...")
    print("=" * 50)
    
    # Agent test
    agent_success = await test_agent()
    print()
    
    # Endpoint test
    endpoint_success = await test_analyze_endpoint()
    print()
    
    # Sonuç
    print("=" * 50)
    if agent_success and endpoint_success:
        print("🎉 Tüm testler başarılı!")
    else:
        print("❌ Bazı testler başarısız!")
    
    return agent_success and endpoint_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
