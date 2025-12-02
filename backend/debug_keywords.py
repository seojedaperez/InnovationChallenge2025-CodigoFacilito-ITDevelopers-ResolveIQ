def categorize(message):
    message_lower = message.lower()
    
    # IT keywords
    it_keywords = ["password", "vpn", "software", "install", "email", "outlook",
                  "computer", "laptop", "network", "printer", "login", "access",
                  "account", "application"]
    
    # HR keywords
    hr_keywords = ["leave", "vacation", "pto", "time off", "payroll", "payslip",
                  "salary", "pay", "holiday", "sick leave", "hr", "benefits"]
    
    # Facilities keywords
    fac_keywords = ["room", "meeting room", "book", "parking", "desk", "chair",
                   "monitor", "equipment", "building", "access card", "badge",
                   "facilities"]
    
    # Legal keywords
    legal_keywords = ["nda", "contract", "agreement", "legal", "compliance",
                     "regulation", "lawyer", "attorney", "policy"]
    
    it_score = sum(1 for kw in it_keywords if kw in message_lower)
    hr_score = sum(1 for kw in hr_keywords if kw in message_lower)
    fac_score = sum(1 for kw in fac_keywords if kw in message_lower)
    legal_score = sum(1 for kw in legal_keywords if kw in message_lower)
    
    scores = {
        "IT": it_score,
        "HR": hr_score,
        "FACILITIES": fac_score,
        "LEGAL": legal_score
    }
    
    print(f"DEBUG: Categorization scores for '{message}': {scores}")
    
    # Return category with highest score
    max_category = max(scores, key=scores.get)
    
    if scores[max_category] == 0:
        return "IT"
        
    return max_category

def test_keywords():
    message = "When do we get paid?"
    category = categorize(message)
    print(f"Message: '{message}'")
    print(f"Category: {category}")
    
    # Debug logic manually
    message_lower = message.lower()
    hr_keywords = ["leave", "vacation", "pto", "time off", "payroll", "payslip",
                  "salary", "pay", "holiday", "sick leave", "hr", "benefits"]
    
    print(f"message_lower: '{message_lower}'")
    for kw in hr_keywords:
        if kw in message_lower:
            print(f"MATCH: '{kw}' in message")
        else:
            print(f"NO MATCH: '{kw}'")

if __name__ == "__main__":
    test_keywords()
