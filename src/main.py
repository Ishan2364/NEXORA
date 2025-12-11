import sys
import os

# --- FIX: Add the project root to the system path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ----------------------------------------------------

from langchain_core.messages import HumanMessage
from src.graph.workflow import create_retail_graph

def main():
    print("🛍️  ABFRL Retail Agent Initializing...")
    
    try:
        app = create_retail_graph()
        print("✅ Agent Graph Built Successfully.")
    except Exception as e:
        print(f"❌ Error building graph: {e}")
        return

    print("💬 Chat with the agent (type 'quit' to exit)")
    print("---------------------------------------------")
    
    # We maintain a simple thread ID for memory
    config = {"configurable": {"thread_id": "1"}}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        try:
            # Stream the graph updates
            for output in app.stream(inputs, config=config):
                for key, value in output.items():
                    
                    # 1. Skip Supervisor/Tool internals (cleaner output)
                    if key == "supervisor" or key == "tools":
                        continue

                    # 2. Get the last message from the active worker agent
                    if "messages" in value and len(value["messages"]) > 0:
                        last_msg = value["messages"][-1]
                        
                        # Check if it's an AI Message with actual text content
                        if hasattr(last_msg, 'content') and last_msg.content:
                            print(f"\n🤖 {key}: {last_msg.content}\n")
                            
        except Exception as e:
            print(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    main()