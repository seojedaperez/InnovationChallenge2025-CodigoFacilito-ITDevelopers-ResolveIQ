import asyncio
import sys
import os

# Add backend to path (current directory)
sys.path.append(os.getcwd())

from src.services.agent_orchestrator import AgentOrchestrator

async def main():
    orchestrator = AgentOrchestrator()
    # No need to fully initialize for this test as we are testing local search
    
    print("Testing Knowledge Base Search...")
    
    # Test 1: Keyword Search
    print("\n--- Test 1: Keyword Search ---")
    queries = ["password", "vacation"]
    for query in queries:
        print(f"Searching for: '{query}'")
        results = await orchestrator.search_knowledge(query)
        for res in results:
            print(f" - [{res['id']}] {res['title']} (Score: {res['relevance']})")

    # Test 2: Category Filter
    print("\n--- Test 2: Category Filter ---")
    categories = ["HR", "IT Support"]
    for cat in categories:
        print(f"Filtering by Category: '{cat}'")
        results = await orchestrator.search_knowledge(category=cat)
        for res in results:
            print(f" - [{res['id']}] {res['title']} ({res['category']})")

    # Test 3: Keyword + Category
    print("\n--- Test 3: Keyword + Category ---")
    print("Searching for 'password' in 'HR' (Should be empty or low relevance)")
    results = await orchestrator.search_knowledge(query="password", category="HR")
    if not results:
        print("No results found (Expected)")
    else:
        for res in results:
            print(f" - [{res['id']}] {res['title']}")

    print("\nSearching for 'password' in 'IT Support'")
    results = await orchestrator.search_knowledge(query="password", category="IT Support")
    for res in results:
        print(f" - [{res['id']}] {res['title']}")

if __name__ == "__main__":
    asyncio.run(main())
