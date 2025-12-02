import requests
import json
import sys

def test_category(message, expected_category):
    url = "http://localhost:5000/api/v1/chat"
    payload = {
        "user_id": "test-user",
        "message": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Testing message: '{message}'")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            actual_category = data.get("category")
            
            if actual_category == expected_category:
                print(f"  PASS: Expected {expected_category}, got {actual_category}")
                return True
            else:
                print(f"  FAIL: Expected {expected_category}, got {actual_category}")
                print(f"  Response: {json.dumps(data, indent=2)}")
                return False
        else:
            print(f"  FAIL: Status code {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  FAIL: Exception {e}")
        return False

def run_tests():
    tests = [
        ("I forgot my password", "IT"),
        ("My laptop is broken", "IT"),
        ("Need to install python", "IT"),
        ("How many vacation days do I have left?", "HR"),
        ("When do we get paid?", "HR"),
        ("I need to book a meeting room", "FACILITIES"),
        ("My chair is broken", "FACILITIES"),
        ("Where is the parking lot?", "FACILITIES"),
        ("I need to review an NDA", "LEGAL"),
        ("Is this contract valid?", "LEGAL"),
        ("Compliance regulation question", "LEGAL"),
        # Ambiguous/Mixed cases (should pick highest score or default)
        ("hello", "IT"), # Default fallback
    ]
    
    passed = 0
    failed = 0
    
    print("=== Starting Backend Classification Verification ===\n")
    
    for message, category in tests:
        if test_category(message, category):
            passed += 1
        else:
            failed += 1
        print("-" * 40)
            
    print(f"\nResults: {passed} Passed, {failed} Failed")
    
    if failed > 0:
        return False
    return True

if __name__ == "__main__":
    if run_tests():
        sys.exit(0)
    else:
        sys.exit(1)
