import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.graph.state import AgentState

# --- 1. FORCE LOAD ENV ---
load_dotenv() 

# --- 2. GET KEY ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Check your .env file.")

# --- IMPORT TOOLS ---
from src.tools.crm_tools import get_customer_profile
from src.tools.inventory_tools import check_inventory
from src.tools.loyalty_tools import calculate_final_price
from src.tools.policy_tools import search_return_policy
from src.tools.catalog_tools import search_catalog

# --- 3. INITIALIZE GROQ ---
llm = ChatGroq(
    model="openai/gpt-oss-120b",  # Powerful and free model
    temperature=0.3,
    api_key=GROQ_API_KEY      # Explicitly pass the key
)

# ... (Rest of your file stays the same: tools binding, sales_node function, etc.)
tools = [get_customer_profile, check_inventory, calculate_final_price, search_return_policy, search_catalog]
llm_with_tools = llm.bind_tools(tools)

def sales_node(state: AgentState):
    # ... (Keep existing logic)
    messages = state["messages"]
    
    system_msg = (
       "You are a top-tier Retail Sales Agent for ABFRL."
       "Your goal is to increase Average Order Value (AOV) by being proactive."
       "\n\n**GUIDELINES:**"
       "\n1. When a user asks for a product, IMMEDIATELY call `search_catalog`."
       "\n2. Then call `check_inventory` for the top items."
       "\n3. Present items with Name, Price, and Store Availability."
    )
    
    if not messages or messages[0].type != "system":
        from langchain_core.messages import SystemMessage
        messages = [SystemMessage(content=system_msg)] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}