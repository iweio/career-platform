from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agents', methods=['GET'])
def list_agents():
    from agents.manager import agent_manager
    return jsonify({"agents": agent_manager.list_agents()})

@app.route('/api/start', methods=['POST'])
def start():
    from agents.manager import agent_manager
    
    agent_id = request.form.get('agent_id', 'resume_extractor')
    user_input = request.form.get('input_text', '')
    doc = request.files.get('doc')
    image = request.files.get('image')
    
    doc_path = ""
    image_path = ""
    
    upload_dir = '/tmp/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    
    if doc:
        doc_path = os.path.join(upload_dir, doc.filename)
        doc.save(doc_path)
    
    if image:
        image_path = os.path.join(upload_dir, image.filename)
        image.save(image_path)
    
    initial_state = {
        "input_text": user_input,
        "file_path": doc_path,
        "image_path": image_path,
        "extracted_text": "",
        "file_text": "",
        "ocr_content": "",
        "merged_text": "",
        "user_profile": {},
        "completeness_flags": {},
        "missing_fields": [],
        "next_question": "",
        "supplement_text": "",
        "supplement_count": 0
    }
    
    result = agent_manager.run_agent(agent_id, initial_state)
    
    if not result.get("success"):
        return jsonify({"step": "error", "message": result.get("error", "未知错误")})
    
    workflow_result = result.get("result", {})
    missing = workflow_result.get("missing_fields", [])
    
    if len(missing) == 0:
        profile = workflow_result.get("user_profile", {})
        import json
        sys.stderr.write(f"[Extract Complete] user_profile: {json.dumps(profile, ensure_ascii=False)}\n")
        sys.stderr.flush()

        try:
            from agents.job_matcher.db_utils import save_user_profile
            save_user_profile(999, profile)
            sys.stderr.write("[Extract Complete] Profile saved to database\n")
        except Exception as e:
            sys.stderr.write(f"[Extract Complete] Failed to save profile: {e}\n")

        return jsonify({
            "step": "complete",
            "profile": profile,
            "user_id": 999,
            "message": "信息已完善！请进行深度分析"
        })
    
    return jsonify({
        "step": "extract",
        "profile": workflow_result.get("user_profile", {}),
        "missing_fields": missing,
        "next_question": workflow_result.get("next_question", ""),
        "merged_text": workflow_result.get("merged_text", ""),
        "message": "请补充以下信息"
    })

@app.route('/api/supplement', methods=['POST'])
def supplement():
    data = request.json
    supplement_text = data.get('supplement_text', '')
    current_profile = data.get('profile', {})
    current_merged = data.get('merged_text', '')
    supplement_count = data.get('supplement_count', 0)

    new_merged = f"{current_merged}\n补充：{supplement_text}"

    from agents.resume_extractor.agent import check_completeness, generate_question

    state = {
        "merged_text": new_merged,
        "user_profile": current_profile,
        "supplement_count": supplement_count + 1,
        "supplement_text": supplement_text
    }

    s2 = check_completeness(state)
    state.update(s2)

    missing = state.get("missing_fields", [])

    if len(missing) == 0:
        profile = state.get("user_profile", {})
        try:
            from agents.job_matcher.db_utils import save_user_profile
            save_user_profile(999, profile)
        except Exception:
            pass

        return jsonify({
            "step": "complete",
            "profile": profile,
            "message": "信息已完善！"
        })

    s3 = generate_question(state)
    state.update(s3)

    return jsonify({
        "step": "continue",
        "profile": state.get("user_profile", {}),
        "missing_fields": missing,
        "next_question": state.get("next_question", ""),
        "merged_text": state.get("merged_text", ""),
        "supplement_count": state.get("supplement_count", 0),
        "message": "请继续补充"
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    data = request.json
    user_profile = data.get('user_profile', {})
    user_id = data.get('user_id', 999)
    print(f"[Analyze] Received user_profile: {user_profile}")

    from agents.manager import agent_manager
    result = agent_manager.run_agent('data_analyzer', {'user_profile': user_profile})

    if not result.get("success"):
        return jsonify({"success": False, "error": result.get("error", "分析失败")})

    agent_result = result.get("result", {})
    deep_analysis = agent_result.get("deep_analysis", {})

    try:
        from agents.job_matcher.db_utils import save_analysis_result
        target_position = deep_analysis.get("recommended_position", "")
        target_company = deep_analysis.get("target_company", "")
        save_analysis_result(user_id, deep_analysis, target_position, target_company)
        print(f"[Analyze] Analysis result saved for user {user_id}")
    except Exception as e:
        print(f"[Analyze] Failed to save analysis: {e}")

    return jsonify({
        "success": True,
        "deep_analysis": deep_analysis,
        "validation_result": agent_result.get("validation_result", {}),
        "report": agent_result.get("report", "")
    })

@app.route('/api/match', methods=['POST'])
def match_jobs():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"success": False, "error": "缺少 user_id 参数"})
    
    from agents.manager import agent_manager
    result = agent_manager.run_agent('job_matcher', {'user_id': user_id})
    
    if not result.get("success"):
        return jsonify({"success": False, "error": result.get("error", "匹配失败")})
    
    agent_result = result.get("result", {})
    match_result = agent_result.get("result", agent_result)
    # 确保返回包含 success 字段
    if "success" not in match_result:
        match_result["success"] = True
    return jsonify(match_result)

@app.route('/api/career_plan', methods=['POST'])
def career_plan():
    data = request.json
    user_id = data.get('user_id', 999)

    try:
        from agents.career_planner.agent import run_career_plan
        result = run_career_plan(user_id=user_id)

        if result.success:
            return jsonify({
                "success": True,
                "top_job": result.top_job,
                "match_score": result.match_score,
                "trends": {
                    "years": result.trends.years,
                    "salary": result.trends.salary,
                    "demand": result.trends.demand,
                    "salary_unit": result.trends.salary_unit,
                    "demand_unit": result.trends.demand_unit
                },
                "career_path": {
                    "current": result.career_path.current,
                    "target": result.career_path.target,
                    "phases": [
                        {
                            "阶段": p.阶段,
                            "目标": p.目标,
                            "能力要求": p.能力要求,
                            "薪资预期": p.薪资预期,
                            "时间节点": p.时间节点
                        } for p in result.career_path.phases
                    ]
                }
            })
        else:
            return jsonify({"success": False, "error": result.error})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/generate', methods=['POST'])
def generate_learning_plan():
    data = request.json
    user_id = data.get('user_id', 999)
    plan_type = data.get('plan_type', '长期')

    try:
        from agents.learning_plan.agent import run_learning_plan
        result = run_learning_plan(user_id, action="generate", plan_type=plan_type)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/polish', methods=['POST'])
def polish_learning_plan():
    data = request.json
    current_plan = data.get('current_plan', {})
    user_feedback = data.get('user_feedback', '')

    try:
        from agents.learning_plan.agent import run_learning_plan
        result = run_learning_plan(0, action="polish", current_plan=current_plan, user_feedback=user_feedback)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/daily_tasks', methods=['POST'])
def generate_daily_tasks():
    data = request.json
    user_id = data.get('user_id', 999)
    phase_index = data.get('phase_index', 0)

    try:
        from agents.learning_plan.agent import run_learning_plan
        result = run_learning_plan(user_id, action="daily_tasks", phase_index=phase_index)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/adjust', methods=['POST'])
def adjust_tasks():
    data = request.json
    user_id = data.get('user_id', 999)

    try:
        from agents.learning_plan.agent import run_learning_plan
        from agents.learning_plan.tools.db_tools import get_daily_tasks

        all_tasks = get_daily_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]
        remaining_tasks = [t for t in all_tasks if t.get("status") != "completed"]

        completed_task_ids = [t["id"] for t in completed_tasks]
        remaining_tasks_formatted = [{
            "id": t["id"],
            "title": t["title"],
            "phase_index": t.get("phase_index", 0)
        } for t in remaining_tasks]

        result = run_learning_plan(user_id, action="adjust",
                                   completed_task_ids=completed_task_ids,
                                   remaining_tasks=remaining_tasks_formatted)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/export', methods=['POST'])
def export_learning_plan():
    data = request.json
    user_id = data.get('user_id', 999)

    try:
        from agents.learning_plan.agent import run_learning_plan
        result = run_learning_plan(user_id, action="export")
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/tasks', methods=['GET'])
def get_daily_tasks():
    user_id = request.args.get('user_id', 999, type=int)

    try:
        from agents.learning_plan.tools.db_tools import get_daily_tasks
        tasks = get_daily_tasks(user_id)
        return jsonify({"success": True, "tasks": tasks})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    status = data.get('status', 'pending')

    try:
        from agents.learning_plan.tools.db_tools import update_task_status
        success = update_task_status(task_id, status)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/learning_plan/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    try:
        from agents.learning_plan.tools.db_tools import update_task_status
        success = update_task_status(task_id, 'completed')
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == '__main__':
    # 初始化 Neo4j 岗位画像数据
    try:
        from agents.job_matcher.db_utils import init_neo4j_job_profiles
        if init_neo4j_job_profiles():
            print("✅ Neo4j 岗位画像数据初始化成功")
        else:
            print("⚠️ Neo4j 岗位画像数据初始化失败")
    except Exception as e:
        print(f"⚠️ 初始化 Neo4j 数据时出错: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
