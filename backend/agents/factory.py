"""
Agent Factory - Farklı agent türlerini oluşturmak için factory pattern
"""

from typing import Dict, Type, Optional
from .cognitive_agent import CognitiveAnalysisAgent
from .config import AgentConfig

class AgentFactory:
    """Agent'ları oluşturmak için factory sınıfı"""
    
    _agents: Dict[str, object] = {}
    _agent_types: Dict[str, Type] = {
        "cognitive": CognitiveAnalysisAgent,
    }
    
    @classmethod
    def create_agent(cls, agent_type: str, **kwargs) -> object:
        """Belirtilen türde agent oluşturur"""
        if agent_type not in cls._agent_types:
            raise ValueError(f"Bilinmeyen agent türü: {agent_type}")
        
        # Eğer agent zaten oluşturulmuşsa, mevcut olanı döndür
        if agent_type in cls._agents:
            return cls._agents[agent_type]
        
        # Yeni agent oluştur
        agent_class = cls._agent_types[agent_type]
        agent = agent_class(**kwargs)
        
        # Cache'e kaydet
        cls._agents[agent_type] = agent
        
        return agent
    
    @classmethod
    def get_agent(cls, agent_type: str) -> Optional[object]:
        """Mevcut agent'ı döndürür"""
        return cls._agents.get(agent_type)
    
    @classmethod
    def clear_agents(cls):
        """Tüm agent'ları temizler"""
        cls._agents.clear()
    
    @classmethod
    def get_available_agents(cls) -> list[str]:
        """Mevcut agent türlerini döndürür"""
        return list(cls._agent_types.keys())
    
    @classmethod
    def get_agent_status(cls) -> Dict[str, bool]:
        """Agent durumlarını döndürür"""
        return {
            agent_type: agent_type in cls._agents 
            for agent_type in cls._agent_types
        }

# Singleton instance
agent_factory = AgentFactory()
