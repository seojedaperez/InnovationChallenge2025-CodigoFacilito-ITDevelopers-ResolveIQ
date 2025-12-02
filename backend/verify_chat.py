import requests
import json
import sys

def test_chat():
    url = "http://localhost:5000/api/v1/chat"
    payload = {
        "user_id": "test-user",
        "message": "I forgot my password"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("SUCCESS: Chat endpoint returned 200 OK")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"FAILURE: Chat endpoint returned {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    if test_chat():
        sys.exit(0)
    else:
        sys.exit(1)
