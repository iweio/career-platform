import json
import re
import os
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .prompts import INTEGRATE_PROMPT, EXTRACT_PROMPT, QUESTION_PROMPT
from .state import CareerPlanningState

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0.1,
    max_tokens=4096,
    timeout=60.0
)

def process_text(state: Dict) -> Dict:
    print("=== 处理文本输入 ===")
    return {"extracted_text": state.get("input_text", "")}

def process_file(state: Dict) -> Dict:
    print("=== 处理上传文件 ===")
    file_path = state.get("file_path", "")
    extracted = ""
    if file_path and os.path.exists(file_path):
        try:
            if file_path.endswith(".pdf"):
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                extracted = "\n".join([d.page_content for d in docs])
            elif file_path.endswith(".docx") or file_path.endswith(".doc"):
                import docx
                doc = docx.Document(file_path)
                extracted = "\n".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"文件解析失败：{e}")
    return {"file_text": extracted}

def process_image(state: Dict) -> Dict:
    print("=== 处理图片 OCR ===")
    image_path = state.get("image_path", "")
    if not image_path or not os.path.exists(image_path):
        return {"ocr_content": ""}
    
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        print(f"OCR识别结果: {text[:100]}...")
        return {"ocr_content": text}
    except Exception as e:
        print(f"OCR失败: {e}")
        return {"ocr_content": ""}

def integrate_info(state: Dict) -> Dict:
    print("=== 整合所有信息 ===")
    input_text = state.get("input_text", "")
    file_text = state.get("file_text", "")
    ocr_content = state.get("ocr_content", "")
    
    all_text = []
    if input_text:
        all_text.append(f"手动输入：{input_text}")
    if file_text:
        all_text.append(f"文档内容：{file_text}")
    if ocr_content:
        all_text.append(f"图片识别：{ocr_content}")
    
    if not all_text:
        merged = "个人信息暂未提供"
    else:
        merged_text = "\n".join(all_text)
        prompt = ChatPromptTemplate.from_messages([
            ("system", INTEGRATE_PROMPT),
            ("user", "待合并信息：{text}")
        ])
        chain = prompt | llm
        res = chain.invoke({"text": merged_text})
        merged = res.content.strip()
    
    print(f"整合结果: {merged[:100]}...")
    return {"merged_text": merged}

def extract_params(state: Dict) -> Dict:
    print("=== AI 抽取结构化信息 ===")
    text = state.get("merged_text", "")
    print(f"待提取文本: {text[:100]}...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", EXTRACT_PROMPT),
        ("user", "用户输入：{text}")
    ])

    chain = prompt | llm
    res = chain.invoke({"text": text})
    content = res.content.strip()
    content = re.sub(r"```json|```", "", content).strip()

    try:
        profile = json.loads(content)
    except Exception as e:
        print(f"JSON解析失败: {e}, content: {content}")
        profile = {}

    dimensions = ["专业技能", "证书", "创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]
    for dim in dimensions:
        if dim not in profile:
            profile[dim] = []

    print(f"提取的profile: {profile}")
    return {"user_profile": profile}

def extract_params_from_text(text: str, current_profile: Dict = None) -> Dict:
    print(f"=== AI 从补充文本抽取信息 ===")
    print(f"补充文本: {text[:100]}...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", EXTRACT_PROMPT),
        ("user", "用户输入：{text}")
    ])

    chain = prompt | llm
    res = chain.invoke({"text": text})
    content = res.content.strip()
    content = re.sub(r"```json|```", "", content).strip()

    try:
        profile = json.loads(content)
    except Exception as e:
        print(f"JSON解析失败: {e}, content: {content}")
        profile = {}

    if current_profile:
        for dim, val in current_profile.items():
            if isinstance(val, dict) and val.get("status") == "已明确" and val.get("details"):
                if dim not in profile:
                    profile[dim] = val
                elif not (isinstance(profile.get(dim), dict) and profile.get(dim).get("status") == "已明确" and profile.get(dim).get("details")):
                    profile[dim] = val

    print(f"从补充文本提取: {profile}")
    return profile

def update_profile_from_text(current_profile: Dict, supplement_text: str) -> Dict:
    updated = current_profile.copy() if current_profile else {}

    keywords = {
        "专业技能": ["Python", "Java", "C++", "JavaScript", "编程", "开发", "技术", "框架", "数据库", "算法"],
        "证书": ["六级", "四级", "证书", "认证", "资格"],
        "创新能力": ["创新", "大赛", "竞赛", "一等奖", "论文", "专利", "立项", "获奖"],
        "学习能力": ["GPA", "成绩", "排名", "奖学金", "学习", "学分"],
        "抗压能力": ["加班", "高压", "抗压", "多项目", "赶进度", "deadline"],
        "沟通能力": ["学生会", "社团", "组织", "活动", "协调", "沟通", "主席", "部长"],
        "实习能力": ["实习", "工作", "项目", "经验", "负责", "腾讯", "阿里", "字节"]
    }

    found = False
    for dim, keys in keywords.items():
        if dim not in updated or not (isinstance(updated.get(dim), dict) and updated.get(dim).get("status") == "已明确"):
            for keyword in keys:
                if keyword in supplement_text:
                    updated[dim] = {"details": [supplement_text], "status": "已明确"}
                    found = True
                    break

    return updated

def check_completeness(state: Dict) -> Dict:
    print("=== 检查信息完整度 ===")
    profile = state.get("user_profile", {})
    dimensions = ["专业技能", "证书", "创新能力", "学习能力", "抗压能力", "沟通能力", "实习能力"]
    
    missing = []
    unclear = []
    flags = {}
    for dim in dimensions:
        dim_data = profile.get(dim, {})
        if isinstance(dim_data, dict):
            status = dim_data.get("status", "")
            if status == "已明确":
                flags[dim] = "complete"
            elif status == "未提及":
                flags[dim] = "missing"
                missing.append(dim)
            else:
                flags[dim] = "unclear"
                unclear.append(dim)
        else:
            flags[dim] = "missing"
            missing.append(dim)
    
    need_question = missing + unclear
    print(f"完整度: {flags}, 需要追问: {need_question}")
    return {"completeness_flags": flags, "missing_fields": need_question}

def analyze_profile(state: Dict) -> Dict:
    print("=== 分析用户画像 ===")
    profile = state.get("user_profile", {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYZE_PROMPT),
        ("user", "{profile}")
    ])
    chain = prompt | llm
    res = chain.invoke({"profile": str(profile)})
    content = res.content.strip()
    content = re.sub(r"```json|```", "", content).strip()
    
    try:
        analysis = json.loads(content)
    except Exception as e:
        print(f"分析结果解析失败: {e}")
        analysis = {}
    
    print(f"分析结果: {analysis}")
    return {"analysis": analysis}

def generate_question(state: Dict) -> Dict:
    print("=== 生成追问问题 ===")
    missing = state.get("missing_fields", [])
    if not missing:
        return {"next_question": ""}
    
    profile = state.get("user_profile", {})
    prompt = ChatPromptTemplate.from_messages([
        ("system", QUESTION_PROMPT),
        ("user", "{profile}")
    ])
    chain = prompt | llm
    res = chain.invoke({"profile": str(profile)})
    return {"next_question": res.content}

def run_workflow(initial_state: Dict) -> Dict:
    """简历信息提取工作流"""
    state = initial_state.copy()
    
    state.update(process_text(state))
    state.update(process_file(state))
    state.update(process_image(state))
    state.update(integrate_info(state))
    state.update(extract_params(state))
    state.update(check_completeness(state))
    
    if state.get("missing_fields"):
        state.update(generate_question(state))
    
    return state
