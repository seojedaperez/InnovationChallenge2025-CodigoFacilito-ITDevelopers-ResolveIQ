import requests
import json

url = "http://localhost:5000/api/v1/tickets"
payload = {
    "description": "Cómo doy de alta a mi pareja en la obra social",
    "user_id": "user-123",
    "channel": "web",
    "priority": "medium"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Category: {data['ticket']['category']}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
