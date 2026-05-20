import urllib.request
import json

print('=== 测试 1: 人岗匹配智能体 ===')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/match',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=60)
    result = json.loads(response.read().decode('utf-8'))
    print('人岗匹配:', '✅ 成功' if result.get('success') else '❌ 失败')
    if result.get('success'):
        match_results = result.get('result', {}).get('match_results', [])
        print(f'  匹配岗位数：{len(match_results)}')
        if match_results:
            best = match_results[0]
            print(f'  最佳匹配：{best.get("job_title")} (分数：{best.get("final_score")})')
    else:
        print(f'  错误：{result.get("error")}')
except Exception as e:
    print(f'人岗匹配：❌ 异常 - {e}')

print()
print('=== 测试 2: 职业规划智能体 ===')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/career_plan',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode('utf-8'))
    print('职业规划:', '✅ 成功' if result.get('success') else '❌ 失败')
    if result.get('success'):
        print(f'  目标岗位：{result.get("top_job")}')
        print(f'  规划阶段数：{len(result.get("phases", []))}')
    else:
        print(f'  错误：{result.get("error")}')
except Exception as e:
    print(f'职业规划：❌ 异常 - {e}')

print()
print('=== 测试 3: 学习计划智能体 ===')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/learning_plan',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode('utf-8'))
    print('学习计划:', '✅ 成功' if result.get('success') else '❌ 失败')
    if result.get('success'):
        phases = result.get('phases', [])
        print(f'  学习阶段数：{len(phases)}')
        tasks = result.get('tasks', [])
        print(f'  每日任务数：{len(tasks)}')
    else:
        print(f'  错误：{result.get("error")}')
except Exception as e:
    print(f'学习计划：❌ 异常 - {e}')
