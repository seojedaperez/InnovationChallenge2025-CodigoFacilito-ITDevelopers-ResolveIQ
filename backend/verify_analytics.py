import asyncio
import sys
import os
import json

# Add backend to path (current directory)
sys.path.append(os.getcwd())

from src.services.agent_orchestrator import AgentOrchestrator

async def main():
    orchestrator = AgentOrchestrator()
    # No need to fully initialize for this test as we are testing local mock data
    
    print("Testing Analytics Metrics...")
    
    try:
        metrics = await orchestrator.get_metrics()
        print("\nMetrics Retrieved Successfully:")
        print(f"Total Tickets: {metrics.total_tickets}")
        print(f"CSAT Score: {metrics.customer_satisfaction_score}")
        print(f"Avg Resolution Time: {metrics.average_resolution_time}")
        
        print("\nTickets by Category:")
        print(json.dumps(metrics.tickets_by_category, indent=2))
        
        print("\nResolution Time Trend (First 2 days):")
        print(json.dumps(metrics.resolution_time_trend[:2], indent=2))
        
        if metrics.customer_satisfaction_score > 0 and len(metrics.resolution_time_trend) > 0:
            print("\nVERIFICATION PASSED: Data structure matches requirements.")
        else:
            print("\nVERIFICATION FAILED: Missing expected data.")
            
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
