import urllib.request
import json

print('=' * 50)
print('📊 智能体功能全面测试')
print('=' * 50)

print('\n【测试 1: 人岗匹配智能体】')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/match',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req, timeout=60)
result = json.loads(response.read().decode('utf-8'))
if 'match_results' in result:
    print('✅ 人岗匹配 - 成功')
    print(f'   匹配岗位数：{len(result["match_results"])}')
    if result['match_results']:
        best = result['match_results'][0]
        print(f'   最佳匹配：{best.get("job_title")} (分数：{best.get("final_score")})')
else:
    print('❌ 人岗匹配 - 失败')
    print(f'   错误：{result.get("error", "Unknown")}')

print('\n【测试 2: 职业规划智能体】')
data = {'user_id': 999}
req = urllib.request.Request(
    'http://localhost:5000/api/career_plan',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(req, timeout=120)
result = json.loads(response.read().decode('utf-8'))
if result.get('success'):
    print('✅ 职业规划 - 成功')
    print(f'   目标岗位：{result.get("top_job")}')
    print(f'   规划阶段数：{len(result.get("phases", []))}')
else:
    print('❌ 职业规划 - 失败')
    print(f'   错误：{result.get("error", "Unknown")}')

print('\n【测试 3: 学习计划智能体】')
data = {'user_id': 999, 'plan_type': '长期'}
req = urllib.request.Request(
    'http://localhost:5000/api/learning_plan/generate',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode('utf-8'))
    if result.get('success'):
        print('✅ 学习计划 - 成功')
        phases = result.get('phases', [])
        print(f'   学习阶段数：{len(phases)}')
        if phases:
            print(f'   第一阶段：{phases[0].get("title", "N/A")}')
    else:
        print('❌ 学习计划 - 失败')
        print(f'   错误：{result.get("error", "Unknown")}')
except Exception as e:
    print('❌ 学习计划 - 异常')
    print(f'   错误：{str(e)}')

print('\n' + '=' * 50)
print('测试完成！')
print('=' * 50)
