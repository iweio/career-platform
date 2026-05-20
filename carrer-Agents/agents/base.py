from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

class AgentBase(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体逻辑"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        pass
    
    def format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化输出"""
        return {
            "success": True,
            "agent": self.name,
            "result": result
        }
    
    def format_error(self, error: str) -> Dict[str, Any]:
        """格式化错误"""
        return {
            "success": False,
            "agent": self.name,
            "error": error
        }
