import os
from dotenv import load_dotenv
from typing import Literal
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field  # Correct Pydantic import
from src.agents.prompts import supervisor_prompt

# 1. FORCE LOAD ENV
load_dotenv()

# 2. GET KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in supervisor.py! Check your .env file.")

# 3. INITIALIZE LLM 
# Use 'llama-3.1-8b-instant' for fast, cheap routing. 
# Temperature 0 is CRITICAL so it strictly follows routing rules.
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY, temperature=0)

# 4. DEFINE ROUTING STRUCTURE
class RouteDecision(BaseModel):
    next_agent: Literal[
        "RecommendationAgent", 
        "InventoryAgent", 
        "LoyaltyAndOffersAgent", 
        "PaymentAgent", 
        "FulfillmentAgent", 
        "PostPurchaseSupportAgent", 
        "END"
    ] = Field(description="The name of the next agent to act.")

# Force the LLM to output ONLY this structure
structured_llm = llm.with_structured_output(RouteDecision)

# 5. THE SUPERVISOR NODE
def supervisor_node(state):
    messages = state["messages"]
    
    # We call the LLM with the supervisor instructions + chat history
    response = structured_llm.invoke([
        {"role": "system", "content": supervisor_prompt},
        *messages
    ])
    
    # Return the decision (e.g., "RecommendationAgent")
    return {"next": response.next_agent}