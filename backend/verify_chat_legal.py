import requests
import json
import sys

def test_chat_legal():
    url = "http://localhost:5000/api/v1/chat"
    payload = {
        "user_id": "test-user",
        "message": "Necesito revisar un NDA para un nuevo proveedor"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Chat endpoint returned 200 OK")
            print(json.dumps(data, indent=2))
            
            # Verify Category
            if data["category"] == "LEGAL":
                print("VERIFICATION PASS: Category is LEGAL")
            else:
                print(f"VERIFICATION FAIL: Category is {data['category']}, expected LEGAL")
                return False
                
            # Verify Grammar
            if "a legal issue" in data["response"].lower() or "a legal query" in data["response"].lower():
                print("VERIFICATION PASS: Grammar 'a legal' found")
            else:
                print("VERIFICATION FAIL: Grammar 'a legal' NOT found")
                return False
                
            return True
        else:
            print(f"FAILURE: Chat endpoint returned {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"FAILURE: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    if test_chat_legal():
        sys.exit(0)
    else:
        sys.exit(1)
