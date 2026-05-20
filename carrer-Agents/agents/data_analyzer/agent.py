import json
import re
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .prompts import ANALYZE_DATA_PROMPT, GENERATE_REPORT_PROMPT

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0.1,
    max_tokens=4096,
    timeout=60.0
)

def validate_input(input_data: Dict[str, Any]) -> bool:
    if not input_data:
        return False
    if "user_profile" not in input_data:
        return False
    return True

def analyze_data(state: Dict) -> Dict:
    print("=== 深度分析用户画像 ===")
    profile = state.get("user_profile", {})
    print(f"输入画像: {profile}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYZE_DATA_PROMPT),
        ("user", "{profile}")
    ])
    chain = prompt | llm
    res = chain.invoke({"profile": str(profile)})
    content = res.content.strip()
    content = re.sub(r"```json|```", "", content).strip()

    try:
        analysis = json.loads(content)
    except Exception as e:
        print(f"分析结果解析失败: {e}, content: {content}")
        analysis = {}

    print(f"深度分析结果: {analysis}")
    return {"deep_analysis": analysis}

def generate_report(state: Dict) -> Dict:
    print("=== 生成职业发展报告 ===")
    profile = state.get("user_profile", {})
    analysis = state.get("deep_analysis", {})

    combined_input = {
        "user_profile": profile,
        "deep_analysis": analysis
    }

    prompt = ChatPromptTemplate.from_messages([
        ("system", GENERATE_REPORT_PROMPT),
        ("user", "{input_data}")
    ])
    chain = prompt | llm
    res = chain.invoke({"input_data": str(combined_input)})
    report = res.content.strip()

    print(f"生成的报告: {report[:100]}...")
    return {"report": report}

def run_workflow(input_data: Dict[str, Any]) -> Dict[str, Any]:
    if not validate_input(input_data):
        return {
            "success": False,
            "error": "输入数据格式错误，需要包含 user_profile 字段"
        }

    state = input_data.copy()
    state.update(analyze_data(state))
    state.update(generate_report(state))

    return {
        "success": True,
        "user_profile": state.get("user_profile", {}),
        "deep_analysis": state.get("deep_analysis", {}),
        "report": state.get("report", "")
    }
