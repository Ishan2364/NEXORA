import sys
import os
import json
from typing import Optional, List

# Fix path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from src.graph.workflow import create_retail_graph
from src.config import DATA_DIR 

# --- INIT ---
app = FastAPI(title="Nexora Retail Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOAD GRAPH ---
try:
    agent_graph = create_retail_graph()
    print("✅ Agent Graph Loaded")
except Exception as e:
    print(f"❌ Graph Error: {e}")
    agent_graph = None

# --- MODELS ---
class ChatRequest(BaseModel):
    message: str
    user_id: str
    platform: str

class LoginRequest(BaseModel):
    username: str
    password: str

class SignupRequest(BaseModel):
    customer_id: str
    name: str
    age: int
    gender: str
    city: str
    device_preference: str = "Mobile"

# --- HELPER FUNCTIONS ---
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.json")

def get_all_customers():
    try:
        with open(CUSTOMERS_FILE, "r") as f:
            return json.load(f).get("customers", [])
    except:
        return []

def save_customer(new_customer):
    try:
        with open(CUSTOMERS_FILE, "r") as f:
            data = json.load(f)
        data["customers"].append(new_customer)
        with open(CUSTOMERS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Save Error: {e}")
        return False

def get_user_invoices(user_id):
    try:
        if not os.path.exists(INVOICE_FILE): return []
        with open(INVOICE_FILE, "r") as f:
            all_inv = json.load(f).get("invoices", [])
        # Filter invoices for this specific customer
        return [i for i in all_inv if i.get("customer_id") == user_id]
    except Exception as e:
        print(f"Invoice Fetch Error: {e}")
        return []

# --- ENDPOINTS ---

@app.post("/login")
async def login(request: LoginRequest):
    clean_user = request.username.strip().upper()
    customers = get_all_customers()
    
    # 1. Find the User
    user = next((c for c in customers if c["customer_id"] == clean_user), None)
    
    if user:
        # 2. Fetch their Invoices
        user_invoices = get_user_invoices(clean_user)
        
        return {
            "status": "success", 
            "user_id": user["customer_id"],
            "real_name": user["name"],
            "tier": user.get("loyalty_tier", "Silver"), 
            "full_profile": user,
            "invoices": user_invoices # <--- Returns invoices to frontend
        }
    
    raise HTTPException(status_code=401, detail="User not found")

@app.post("/signup")
async def signup(request: SignupRequest):
    customers = get_all_customers()
    
    # Check duplicate
    if any(c["customer_id"] == request.customer_id.upper() for c in customers):
        raise HTTPException(status_code=400, detail="Customer ID already exists")
    
    # Create new profile
    new_profile = {
        "customer_id": request.customer_id.upper(),
        "name": request.name,
        "age": request.age,
        "gender": request.gender,
        "city": request.city,
        "loyalty_tier": "Silver",
        "device_preference": request.device_preference,
        "purchase_history": []
    }
    
    if save_customer(new_profile):
        return {"status": "success", "message": "Profile created"}
    
    raise HTTPException(status_code=500, detail="Failed to save profile")

@app.post("/chat")
async def chat(request: ChatRequest):
    if not agent_graph: raise HTTPException(status_code=500, detail="Graph not ready")
    
    try:
        inputs = {"messages": [HumanMessage(content=request.message)]}
        config = {"configurable": {"thread_id": request.user_id}}
        final_res = "I'm thinking..."
        
        for event in agent_graph.stream(inputs, config=config):
            for key, val in event.items():
                if val is not None and key not in ["supervisor", "tools", "trimmer"] and "messages" in val:
                    last = val["messages"][-1]
                    if hasattr(last, 'content'): final_res = last.content
                    
        return {"response": final_res}
    except Exception as e:
        return {"response": "⚠️ System busy."}