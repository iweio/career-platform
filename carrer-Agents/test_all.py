import urllib.request
import json

print('=== 测试 1: 人岗匹配 ===')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/match',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req, timeout=60)
result = json.loads(response.read().decode('utf-8'))
status = '✅ 成功' if 'match_results' in result else '❌ 失败'
print(f'状态：{status}')
if 'match_results' in result:
    count = len(result['match_results'])
    print(f'匹配岗位数：{count}')
    if result['match_results']:
        best = result['match_results'][0]
        job_title = best.get('job_title', 'N/A')
        score = best.get('final_score', 'N/A')
        print(f'最佳匹配：{job_title} (分数：{score})')

print()
print('=== 测试 2: 职业规划 ===')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/career_plan',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req, timeout=120)
result = json.loads(response.read().decode('utf-8'))
status = '✅ 成功' if result.get('success') else '❌ 失败'
print(f'状态：{status}')
if result.get('success'):
    top_job = result.get('top_job', 'N/A')
    phases_count = len(result.get('phases', []))
    print(f'目标岗位：{top_job}')
    print(f'规划阶段数：{phases_count}')

print()
print('=== 测试 3: 学习计划生成 ===')
data = {'user_id': 999, 'plan_type': '长期'}
req = urllib.request.Request(
    'http://localhost:5000/api/learning_plan/generate',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode('utf-8'))
    status = '✅ 成功' if result.get('success') else '❌ 失败'
    print(f'状态：{status}')
    if result.get('success'):
        phases = result.get('phases', [])
        print(f'学习阶段数：{len(phases)}')
        if phases:
            first_phase = phases[0].get('title', 'N/A')
            print(f'第一阶段：{first_phase}')
except Exception as e:
    print(f'状态：❌ 失败 - {e}')
