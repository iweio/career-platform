from typing import Dict, Any, Optional

class AgentManager:
    """智能体管理器"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self._register_agents()
    
    def _register_agents(self):
        """注册所有智能体"""
        from agents.resume_extractor import run_workflow as resume_run
        self.agents["resume_extractor"] = {
            "name": "简历信息提取",
            "description": "从文本、文档、图片中提取简历信息并结构化",
            "run": resume_run
        }
        
        from agents.data_analyzer import run_workflow as analyzer_run
        self.agents["data_analyzer"] = {
            "name": "数据分析师",
            "description": "对简历提取的结构化数据进行深度分析，生成职业发展报告",
            "run": analyzer_run
        }

        from agents.job_matcher import run_workflow as matcher_run
        self.agents["job_matcher"] = {
            "name": "人岗匹配",
            "description": "根据用户画像和岗位要求进行人岗匹配分析，生成匹配分数和差距报告",
            "run": matcher_run
        }
        
        # 预留其他智能体
    
    def list_agents(self) -> list:
        """列出所有智能体"""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in self.agents.items()
        ]
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取智能体"""
        return self.agents.get(agent_id)
    
    def run_agent(self, agent_id: str, input_data: Dict) -> Dict:
        """运行智能体"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"success": False, "error": f"智能体 {agent_id} 不存在"}
        
        if not agent["run"]:
            return {"success": False, "error": f"智能体 {agent_id} 尚未实现"}
        
        try:
            result = agent["run"](input_data)
            return {"success": True, "agent": agent_id, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

agent_manager = AgentManager()
