"""
ChromaDB Servisi - Semantik arama ve vektör veritabanı yönetimi
"""

import os
import chromadb
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class ChromaService:
    """ChromaDB client servisi"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """ChromaDB client'ını başlatır"""
        try:
            # Persist directory'yi belirle
            if persist_directory is None:
                persist_directory = os.path.join(os.getcwd(), "chroma_db")
            
            # ChromaDB client'ı oluştur
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Embedding fonksiyonu (sentence-transformers)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="paraphrase-multilingual-MiniLM-L12-v2"  # Türkçe destekli model
            )
            
            # Koleksiyonları başlat
            self._initialize_collections()
            
            logger.info(f"ChromaDB başarıyla başlatıldı: {persist_directory}")
            
        except Exception as e:
            logger.error(f"ChromaDB başlatma hatası: {e}")
            raise
    
    def _initialize_collections(self):
        """Gerekli koleksiyonları oluşturur"""
        try:
            # 1. Kullanıcı günlük yazıları koleksiyonu
            self.entries_collection = self.client.get_or_create_collection(
                name="user_entries",
                embedding_function=self.embedding_function,
                metadata={"description": "Kullanıcı günlük yazıları ve analizleri"}
            )
            
            # 2. Terapi teknikleri koleksiyonu
            self.techniques_collection = self.client.get_or_create_collection(
                name="therapy_techniques",
                embedding_function=self.embedding_function,
                metadata={"description": "BDT teknikleri ve egzersizleri"}
            )
            
            # 3. Analiz sonuçları koleksiyonu
            self.analysis_collection = self.client.get_or_create_collection(
                name="analysis_results",
                embedding_function=self.embedding_function,
                metadata={"description": "Çarpıtma analizleri ve sonuçları"}
            )
            
            logger.info("ChromaDB koleksiyonları başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"Koleksiyon başlatma hatası: {e}")
            raise
    
    # ----- USER ENTRIES -----
    
    async def add_user_entry(
        self, 
        entry_id: str, 
        user_id: str, 
        text: str, 
        analysis_result: Dict[str, Any],
        mood_score: Optional[int] = None
    ) -> bool:
        """Kullanıcı girişini ChromaDB'ye ekler"""
        try:
            # Metadata hazırla
            metadata = {
                "user_id": user_id,
                "entry_id": entry_id,
                "mood_score": mood_score or 5,
                "created_at": datetime.now().isoformat(),
                "distortions": ",".join([d.get("type", "") for d in analysis_result.get("distortions", [])]),
                "overall_mood": analysis_result.get("overall_mood", "neutral"),
                "risk_level": analysis_result.get("risk_level", "low")
            }
            
            # Vektöre çevrilecek text hazırla
            document_text = f"{text}\n\nAnaliz: {analysis_result.get('overall_mood', '')}"
            
            # ChromaDB'ye ekle
            self.entries_collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[f"entry_{entry_id}_{user_id}"]
            )
            
            logger.info(f"Entry {entry_id} ChromaDB'ye eklendi")
            return True
            
        except Exception as e:
            logger.error(f"Entry ekleme hatası: {e}")
            return False
    
    async def find_similar_entries(
        self, 
        user_id: str, 
        query_text: str, 
        n_results: int = 5,
        distortion_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Benzer kullanıcı girişlerini bulur"""
        try:
            # Sadece user_id ile filtrele (distortion_type filtrelemesini kaldır)
            where_filter = {"user_id": user_id}
            
            # Semantik arama yap
            results = self.entries_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
            
            # Sonuçları formatla
            similar_entries = []
            for i in range(len(results['documents'][0])):
                similar_entries.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i]  # Distance'ı similarity'ye çevir
                })
            
            return similar_entries
            
        except Exception as e:
            logger.error(f"Benzer entry bulma hatası: {e}")
            return []
    
    # ----- THERAPY TECHNIQUES -----
    
    async def add_therapy_technique(
        self, 
        technique_id: str, 
        technique_data: Dict[str, Any], 
        distortion_type: str
    ) -> bool:
        """Terapi tekniğini ChromaDB'ye ekler"""
        try:
            # Technique text hazırla
            technique_text = f"""
            Başlık: {technique_data.get('title', '')}
            Açıklama: {technique_data.get('description', '')}
            Egzersiz: {technique_data.get('exercise', '')}
            Çarpıtma Türü: {distortion_type}
            """
            
            # Metadata hazırla
            metadata = {
                "technique_id": technique_id,
                "distortion_type": distortion_type,
                "title": technique_data.get('title', ''),
                "difficulty": technique_data.get('difficulty', 'orta'),
                "duration": technique_data.get('duration', ''),
                "added_at": datetime.now().isoformat()
            }
            
            # ChromaDB'ye ekle
            self.techniques_collection.add(
                documents=[technique_text],
                metadatas=[metadata],
                ids=[technique_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Technique ekleme hatası: {e}")
            return False
    
    async def find_relevant_techniques(
        self, 
        query_text: str, 
        distortion_types: List[str] = None, 
        n_results: int = 3,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """İlgili terapi tekniklerini bulur"""
        try:
            # Basit filtre - sadece tek condition
            where_filter = None
            if distortion_types and len(distortion_types) == 1:
                # Tek distortion type için basit filtre
                where_filter = {"distortion_type": distortion_types[0]}
            elif difficulty:
                where_filter = {"difficulty": difficulty}
            
            # Semantik arama yap
            results = self.techniques_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_filter
            )
            
            # Sonuçları formatla
            relevant_techniques = []
            for i in range(len(results['documents'][0])):
                relevant_techniques.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "relevance_score": 1 - results['distances'][0][i]
                })
            
            return relevant_techniques
            
        except Exception as e:
            logger.error(f"Technique bulma hatası: {e}")
            return []
    
    # ----- ANALYSIS RESULTS -----
    
    async def add_analysis_result(
        self, 
        analysis_id: str, 
        user_id: str, 
        entry_text: str, 
        analysis_data: Dict[str, Any]
    ) -> bool:
        """Analiz sonucunu ChromaDB'ye ekler"""
        try:
            # Analysis text hazırla
            distortions_text = "\n".join([
                f"- {d.get('type', '')}: {d.get('explanation', '')}"
                for d in analysis_data.get('distortions', [])
            ])
            
            analysis_text = f"""
            Giriş: {entry_text}
            
            Tespit Edilen Çarpıtmalar:
            {distortions_text}
            
            Genel Ruh Hali: {analysis_data.get('overall_mood', '')}
            Risk Seviyesi: {analysis_data.get('risk_level', '')}
            """
            
            # Metadata hazırla
            metadata = {
                "analysis_id": analysis_id,
                "user_id": user_id,
                "distortion_count": len(analysis_data.get('distortions', [])),
                "distortion_types": ",".join([d.get("type", "") for d in analysis_data.get("distortions", [])]),
                "overall_mood": analysis_data.get('overall_mood', ''),
                "risk_level": analysis_data.get('risk_level', ''),
                "analyzed_at": datetime.now().isoformat()
            }
            
            # ChromaDB'ye ekle
            self.analysis_collection.add(
                documents=[analysis_text],
                metadatas=[metadata],
                ids=[analysis_id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Analysis ekleme hatası: {e}")
            return False
    
    # ----- ANALYTICS -----
    
    async def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Kullanıcının düşünce kalıplarını analiz eder"""
        try:
            # Kullanıcının tüm analiz sonuçlarını al
            results = self.analysis_collection.get(
                where={"user_id": user_id}
            )
            
            if not results['metadatas']:
                return {"message": "Henüz yeterli veri yok"}
            
            # İstatistikleri hesapla
            distortion_counts = {}
            mood_distribution = {}
            risk_levels = {}
            
            for metadata in results['metadatas']:
                # Çarpıtma türleri
                if metadata.get('distortion_types'):
                    for dtype in metadata['distortion_types'].split(','):
                        if dtype.strip():
                            distortion_counts[dtype.strip()] = distortion_counts.get(dtype.strip(), 0) + 1
                
                # Ruh hali dağılımı
                mood = metadata.get('overall_mood', 'unknown')
                mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
                
                # Risk seviyeleri
                risk = metadata.get('risk_level', 'unknown')
                risk_levels[risk] = risk_levels.get(risk, 0) + 1
            
            return {
                "total_analyses": len(results['metadatas']),
                "most_common_distortions": sorted(distortion_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "mood_distribution": mood_distribution,
                "risk_level_distribution": risk_levels,
                "analysis_period": {
                    "first_analysis": min([m.get('analyzed_at', '') for m in results['metadatas']]),
                    "last_analysis": max([m.get('analyzed_at', '') for m in results['metadatas']])
                }
            }
            
        except Exception as e:
            logger.error(f"Pattern analizi hatası: {e}")
            return {"error": "Pattern analizi yapılamadı"}
    
    # ----- UTILITY -----
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Koleksiyon istatistiklerini döndürür"""
        try:
            stats = {
                "entries": self.entries_collection.count(),
                "techniques": self.techniques_collection.count(),
                "analyses": self.analysis_collection.count(),
                "timestamp": datetime.now().isoformat()
            }
            return stats
            
        except Exception as e:
            logger.error(f"Stats hatası: {e}")
            return {"error": "İstatistikler alınamadı"}
    
    async def clear_user_data(self, user_id: str) -> bool:
        """Kullanıcının tüm verilerini temizler"""
        try:
            # Entries
            self.entries_collection.delete(where={"user_id": user_id})
            
            # Analyses  
            self.analysis_collection.delete(where={"user_id": user_id})
            
            logger.info(f"Kullanıcı {user_id} verileri temizlendi")
            return True
            
        except Exception as e:
            logger.error(f"Veri temizleme hatası: {e}")
            return False


# Global instance
chroma_service = None

def get_chroma_service() -> ChromaService:
    """ChromaService singleton instance'ını döndürür"""
    global chroma_service
    if chroma_service is None:
        chroma_service = ChromaService()
    return chroma_service
