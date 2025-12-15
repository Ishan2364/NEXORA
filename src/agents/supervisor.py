from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import Literal
import os
from dotenv import load_dotenv

# --- IMPORT THE DETAILED PROMPT ---
from src.agents.prompts import supervisor_prompt

load_dotenv()

# --- 1. SETUP LLM ---
llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

members = ["RecommendationAgent", "InventoryAgent", "LoyaltyAndOffersAgent", "PaymentAgent", "FulfillmentAgent", "PostPurchaseSupportAgent"]

# --- 2. DEFINE OUTPUT SCHEMA (Pydantic Fix) ---
class Route(BaseModel):
    """Select the next role."""
    next: str = Field(description="The next worker to act or FINISH")

# --- 3. CONSTRUCT PROMPT ---
# We use the imported 'supervisor_prompt' which contains all your logic/rules
prompt = ChatPromptTemplate.from_messages([
    ("system", supervisor_prompt),
    MessagesPlaceholder(variable_name="messages"),
    # A final nudge to ensure it picks a valid name
    ("system", "Based on the conversation and the rules above, who should act next? Select one of: {members} or FINISH."),
]).partial(members=", ".join(members))

# --- 4. CREATE CHAIN ---
supervisor_chain = prompt | llm.with_structured_output(Route)

def supervisor_node(state):
    try:
        result = supervisor_chain.invoke(state)
        next_agent = result.next if result else "FINISH"
        
        # Safety Check: If LLM hallucinates a name, default to safe browsing
        if next_agent not in members and next_agent != "FINISH":
            print(f"⚠️ Invalid Route Detected: {next_agent} -> Defaulting to RecommendationAgent")
            next_agent = "RecommendationAgent"
            
        return {"next": next_agent}
        
    except Exception as e:
        print(f"❌ Supervisor Error: {e}")
        # Fail gracefully
        return {"next": "RecommendationAgent"}