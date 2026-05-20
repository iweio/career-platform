from typing import Dict, Any

def run_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    user_id = input_data.get("user_id")
    if user_id is None:
        return {"success": False, "error": "缺少 user_id 参数"}

    try:
        from .match_agent import run_match
        result = run_match(user_id)
        if "error" in result:
            return {"success": False, "error": result["error"]}
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
