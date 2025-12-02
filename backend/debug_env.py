import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from config.settings import settings

def check_settings():
    print(f"BASE_DIR: {settings.BASE_DIR}")
    env_path = settings.BASE_DIR / ".env"
    print(f"Expected .env path: {env_path}")
    print(f"Does .env exist? {env_path.exists()}")
    
    api_key = settings.AZURE_OPENAI_API_KEY
    if api_key:
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
        print(f"AZURE_OPENAI_API_KEY: Found ({masked_key})")
    else:
        print("AZURE_OPENAI_API_KEY: Not found or empty")
        
    print(f"AZURE_OPENAI_ENDPOINT: {settings.AZURE_OPENAI_ENDPOINT}")

if __name__ == "__main__":
    check_settings()
