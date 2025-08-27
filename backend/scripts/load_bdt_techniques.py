"""
BDT Tekniklerini ChromaDB'ye Yükler
Bu script mevcut BDT_TECHNIQUES sözlüğündeki teknikleri ChromaDB'ye aktarır.
"""

import os
import asyncio
import logging
import sys

# Backend root dizinini ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.chroma_service import get_chroma_service
from agents.rag_agent import BDT_TECHNIQUES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_bdt_techniques():
    """BDT tekniklerini ChromaDB'ye yükler"""
    try:
        # ChromaDB servisi
        chroma_service = get_chroma_service()
        
        logger.info("BDT teknikleri ChromaDB'ye yükleniyor...")
        
        total_techniques = 0
        loaded_techniques = 0
        
        # Her çarpıtma türü için
        for distortion_type, distortion_data in BDT_TECHNIQUES.items():
            logger.info(f"İşleniyor: {distortion_data['name']}")
            
            # Her teknik için
            for idx, technique in enumerate(distortion_data['techniques']):
                technique_id = f"{distortion_type}_{idx}"
                total_techniques += 1
                
                # ChromaDB'ye ekle
                success = await chroma_service.add_therapy_technique(
                    technique_id=technique_id,
                    technique_data=technique,
                    distortion_type=distortion_type
                )
                
                if success:
                    loaded_techniques += 1
                    logger.info(f"{technique['title']} -> ChromaDB")
                else:
                    logger.error(f"{technique['title']} -> Hata!")
        
        logger.info(f"Özet: {loaded_techniques}/{total_techniques} teknik yüklendi")
        
        # İstatistikler
        stats = await chroma_service.get_collection_stats()
        logger.info(f"ChromaDB İstatistikleri: {stats.get('techniques', 0)} teknik, {stats.get('entries', 0)} entry")
        
        return loaded_techniques == total_techniques
        
    except Exception as e:
        logger.error(f"BDT yükleme hatası: {e}")
        return False


async def test_technique_search():
    """Teknik arama testı"""
    try:
        logger.info("Teknik arama testi...")
        
        chroma_service = get_chroma_service()
        
        # Test sorguları
        test_queries = [
            ("üzgün hissediyorum", ["felaketleştirme", "kişiselleştirme"]),
            ("herkes benden nefret ediyor", ["zihin okuma", "genelleme"]),
            ("hiçbir şey yapamıyorum", ["ya hep ya hiç", "etiketleme"])
        ]
        
        for query, expected_types in test_queries:
            logger.info(f"Sorgu: '{query}'")
            
            techniques = await chroma_service.find_relevant_techniques(
                query_text=query,
                distortion_types=expected_types,
                n_results=2
            )
            
            for tech in techniques:
                metadata = tech['metadata']
                score = tech['relevance_score']
                logger.info(f"  {metadata['title']} ({metadata['distortion_type']}) - Skor: {score:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test hatası: {e}")
        return False


async def main():
    """Ana fonksiyon"""
    logger.info("ChromaDB BDT Teknik Yükleyici başlatıldı")
    
    # 1. Teknikleri yükle
    load_success = await load_bdt_techniques()
    
    if load_success:
        logger.info("Teknikler başarıyla yüklendi!")
        
        # 2. Test et
        test_success = await test_technique_search()
        
        if test_success:
            logger.info("Testler başarılı! ChromaDB hazır.")
        else:
            logger.warning("Testlerde sorun var.")
    else:
        logger.error("Teknik yükleme başarısız!")
    
    logger.info("ChromaDB yükleme işlemi tamamlandı")


if __name__ == "__main__":
    asyncio.run(main())
