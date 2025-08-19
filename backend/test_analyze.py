#!/usr/bin/env python3
"""
Analyze Endpoint Test Script
"""

import requests
import json

def test_analyze_endpoint():
    """Analyze endpoint'ini test eder"""
    
    # Test URL
    url = "http://localhost:8000/analyze/"
    
    # Test data
    test_data = {
        "text": "Bugün çok kötü bir gün. Hiçbir şey yolunda gitmiyor.",
        "user_id": "test_user_123"
    }
    
    print("🧪 Analyze endpoint test ediliyor...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        # POST request
        response = requests.post(url, json=test_data)
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Başarılı! Sonuç:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Hata! Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Bağlantı hatası: Backend çalışmıyor olabilir")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

def test_health_endpoint():
    """Health endpoint'ini test eder"""
    
    url = "http://localhost:8000/analyze/health"
    
    print(f"\n🏥 Health endpoint test ediliyor...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check başarılı:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Health check hatası: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check hatası: {e}")

if __name__ == "__main__":
    print("🚀 Analyze Endpoint Test Başlıyor...")
    print("=" * 50)
    
    test_analyze_endpoint()
    test_health_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Test tamamlandı!")
