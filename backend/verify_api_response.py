import requests
import json

url = "http://localhost:5000/api/v1/chat"
payload = {
    "user_id": "test-user",
    "message": "password reset"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Response Keys:", data.keys())
        if "kb_articles" in data:
            print(f"Category detected: {data.get('category')}")
            print(f"kb_articles count: {len(data['kb_articles'])}")
            print("kb_articles data:", json.dumps(data['kb_articles'], indent=2))
        else:
            print("ERROR: kb_articles field is MISSING from response")
    else:
        print("Error Response:", response.text)
except Exception as e:
    print(f"Request failed: {e}")
