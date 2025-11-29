import asyncio
import logging
import sys
from src.services.content_safety_service import get_content_safety_service

# Configure logging to see errors
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test_safety():
    print("Initializing Content Safety Service...")
    service = get_content_safety_service()
    
    if not service.client:
        print("Client is None (Fallback mode)")
        from src.config.settings import settings
        print(f"Key loaded? {'Yes' if settings.AZURE_CONTENT_SAFETY_KEY else 'No'}")
        print(f"Endpoint: {settings.AZURE_CONTENT_SAFETY_ENDPOINT}")
    else:
        print("Client initialized")
        
    text = "I cannot access my email"
    print(f"Analyzing text: '{text}'")
    
    result = await service.analyze_text(text)
    
    print("\n--- Result ---")
    print(f"Is Safe: {result.is_safe}")
    print(f"Blocked Reason: {result.blocked_reason}")
    print(f"Hate Score: {result.hate_score}")
    print(f"Self Harm Score: {result.self_harm_score}")
    print(f"Sexual Score: {result.sexual_score}")
    print(f"Violence Score: {result.violence_score}")

if __name__ == "__main__":
    asyncio.run(test_safety())
