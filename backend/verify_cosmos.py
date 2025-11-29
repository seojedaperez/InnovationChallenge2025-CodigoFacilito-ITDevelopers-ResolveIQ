import asyncio
import logging
import sys
import uuid
from src.services.cosmos_service import get_cosmos_service
from src.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

async def verify_cosmos():
    print(f"Checking Cosmos DB Configuration...")
    print(f"Endpoint: {settings.AZURE_COSMOS_ENDPOINT}")
    print(f"Database: {settings.AZURE_COSMOS_DATABASE_NAME}")
    print(f"Key Configured: {'Yes' if settings.AZURE_COSMOS_KEY else 'No'}")

    if not settings.AZURE_COSMOS_KEY:
        print("[X] AZURE_COSMOS_KEY is missing in .env. Cannot connect to real database.")
        return

    print("\nInitializing Cosmos Service...")
    service = get_cosmos_service()
    
    if not service.client:
        print("[X] Failed to initialize Cosmos Client (check logs above).")
        return

    print("[OK] Client initialized.")

    # Test Data
    test_id = str(uuid.uuid4())
    test_item = {
        "id": test_id,
        "user_id": "test-user",
        "userId": "test-user", # Required for Partition Key
        "description": "Cosmos DB Verification Test",
        "status": "test"
    }

    try:
        print(f"\nAttempting to create test ticket {test_id}...", flush=True)
        # We use the container client directly to avoid Pydantic model complexity for this simple test
        container = service.database.get_container_client("tickets")
        
        # Check Partition Key Definition
        properties = container.read()
        pk_path = properties['partitionKey']['paths'][0]
        print(f"Container Partition Key Path: {pk_path}", flush=True)
        
        container.create_item(body=test_item)
        print("[OK] Item created successfully.", flush=True)

        print("Waiting 2 seconds for propagation...", flush=True)
        await asyncio.sleep(2)

        print("Attempting to read item back...", flush=True)
        read_item = container.read_item(item=test_id, partition_key="test-user")
        print(f"[OK] Item read successfully: {read_item['description']}", flush=True)

        print("Attempting to delete item...", flush=True)
        container.delete_item(item=test_id, partition_key="test-user")
        print("[OK] Item deleted successfully.", flush=True)

        print("\n[SUCCESS] COSMOS DB IS FULLY FUNCTIONAL!", flush=True)

    except Exception as e:
        print(f"\n[ERROR] Cosmos DB Operation Failed: {e}", flush=True)
        print("Tip: Check if your IP address is allowed in the Azure Cosmos DB Firewall settings.", flush=True)

if __name__ == "__main__":
    asyncio.run(verify_cosmos())
