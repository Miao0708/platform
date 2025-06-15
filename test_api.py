import requests
import json

# 测试后端API
def test_api():
    base_url = "http://127.0.0.1:8000/api/v1"
    
    # 测试GET请求
    print("测试GET /ai/prompts...")
    try:
        response = requests.get(f"{base_url}/ai/prompts")
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"GET Error: {e}")
    
    # 测试POST请求
    print("\n测试POST /ai/prompts...")
    try:
        data = {
            "name": "测试Prompt",
            "content": "这是测试内容",
            "description": "测试描述",
            "category": "general",
            "tags": ["测试"]
        }
        response = requests.post(f"{base_url}/ai/prompts", json=data)
        print(f"POST Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"POST Error: {e}")

if __name__ == "__main__":
    test_api() 