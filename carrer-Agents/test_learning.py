import urllib.request
import json

print('=== 测试学习计划生成 ===')
data = {'user_id': 999, 'plan_type': '长期'}
req = urllib.request.Request(
    'http://localhost:5000/api/learning_plan/generate',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    result = json.loads(response.read().decode('utf-8'))
    print('Response:', json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()
