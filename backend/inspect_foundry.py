import sys
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

# Load env vars
load_dotenv()

connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")

def test_inference():
    if not connection_string:
        print("Connection string not found")
        return

    try:
        client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=connection_string,
        )
        
        inference_client = client.inference.get_chat_completions_client()
        
        # Try a simple completion
        response = inference_client.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4o", # Assuming this deployment exists as per .env
            max_tokens=10
        )
        
        print(f"Response: {response.choices[0].message.content}")
             
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_inference()
