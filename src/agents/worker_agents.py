import os
import json
from typing import Union
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from src.graph.state import AgentState
from src.config import DATA_DIR  # Import to find products.json
# ... inside the imports ...
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ADD THIS TEMPORARY CHECK
print(f"DEBUG: Loaded Key starts with: {GROQ_API_KEY[:5]}...") 

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing.")
# Import prompts
from src.agents.prompts import (
    recommendation_prompt, inventory_prompt, loyalty_prompt, 
    payment_prompt, full_prompt as fulfillment_prompt, post_prompt
)

# Import real logic tools
from src.tools.inventory_tools import check_inventory_status
from src.tools.catalog_tools import search_catalog
from src.tools.loyalty_tools import calculate_final_price
from src.tools.crm_tools import get_customer_profile 
from src.tools.policy_tools import search_return_policy

# --- 1. SETUP ENV ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

# Using Instant model for speed/stability
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY, temperature=0)

# --- 2. DEFINE TOOLS ---

import json
import os
from datetime import datetime
from src.config import DATA_DIR

# --- HELPER: Invoice Storage ---
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.json")

def save_invoice_to_db(invoice_data):
    try:
        if not os.path.exists(INVOICE_FILE):
            with open(INVOICE_FILE, "w") as f: json.dump({"invoices": []}, f)
            
        with open(INVOICE_FILE, "r") as f:
            db = json.load(f)
            
        db["invoices"].append(invoice_data)
        
        with open(INVOICE_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Invoice Save Error: {e}")

# --- NEW TOOL ---
@tool
def generate_invoice(order_id: str, customer_id: str, amount: float, items_summary: str):
    """
    Generates an invoice, saves it to the backend, and returns data for the frontend.
    Args:
        order_id: The ID of the order (e.g. ORD-123)
        customer_id: The user's ID (e.g. CUST001)
        amount: Total amount paid.
        items_summary: Short description of items (e.g. "2x Jeans, 1x Top")
    """
    invoice_data = {
        "invoice_id": f"INV-{int(datetime.now().timestamp())}",
        "order_id": order_id,
        "customer_id": customer_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "items": items_summary,
        "status": "Paid"
    }
    
    # 1. Save to Backend File
    save_invoice_to_db(invoice_data)
    
    # 2. Return Data Tag for Frontend
    return f"||INVOICE_DATA:{json.dumps(invoice_data)}||"
    
    # Return as a compact JSON string wrapped in our secret tag
    return f"||INVOICE:{json.dumps(invoice_data)}||"

@tool
def add_to_cart(product_sku: str, quantity: int = 1):
    """Adds a specific product SKU to the customer's shopping cart."""
    return json.dumps({
        "status": "success", 
        "message": f"Added SKU {product_sku} to cart.", 
        "sku": product_sku, 
        "quantity": quantity
    })

@tool
def find_products(gender: str = None, category: str = None, sub_category: str = None, max_price: float = None):
    """Searches for products based on category/filters."""
    query = f"{gender or ''} {category or ''} {sub_category or ''}".strip()
    return search_catalog.invoke({"query": query})

@tool
def search_products(query: str):
    """Searches products by text query."""
    return search_catalog.invoke({"query": query})

@tool
def get_product_details_for_comparison(product_ids: list):
    """Gets details for comparison."""
    return search_catalog.invoke({"query": " ".join(product_ids)})

@tool
def get_cross_sell_products(product_id: str):
    """Gets cross-sell recommendations."""
    return search_catalog.invoke({"query": "accessories"})

@tool
def request_back_in_stock_notification(customer_id: str, product_sku: str):
    """Registers a notification request."""
    return json.dumps({"status": "success", "message": f"Notification set for {product_sku}"})

@tool
def update_inventory_stock(product_sku: str, location_id: str, quantity_sold: int):
    """Updates stock after sale."""
    return json.dumps({"status": "success", "new_count": 0}) 

@tool
def get_active_promotions():
    """Returns active promotions."""
    return json.dumps([{"threshold": 5000, "description": "Flat ₹500 off >5k"}])

# --- CRITICAL FIX: Smart Price Lookup ---
# ... (inside src/agents/worker_agents.py)

@tool
def calculate_final_pricing(cart_items: Union[list, str], loyalty_tier: str = "Bronze", coupon_codes: Union[list, str] = None):
    """
    Calculates final price. 
    Args:
        cart_items: List of SKUs or item dicts.
        loyalty_tier: The user's tier (e.g. "Gold", "Platinum"). 
    """
    
    # 1. Parse Inputs
    def parse_input(data, expected_type):
        if isinstance(data, str):
            try:
                return json.loads(data)
            except:
                return expected_type() 
        return data or expected_type()

    raw_items = parse_input(cart_items, list)
    
    # 2. Load Catalog to Lookup Prices
    products_file = os.path.join(DATA_DIR, "products.json")
    try:
        with open(products_file, "r") as f:
            catalog = json.load(f)
        price_map = {str(p["sku"]): p["price"] for p in catalog}
    except Exception:
        price_map = {}

    # 3. Calculate Total
    total = 0
    for item in raw_items:
        if isinstance(item, str):
            price = price_map.get(item, 0)
            qty = 1
        elif isinstance(item, dict):
            price = item.get("price")
            if price is None:
                sku = str(item.get("product_sku") or item.get("sku") or "")
                price = price_map.get(sku, 0)
            qty = item.get("quantity", 1)
        else:
            price = 0
            qty = 0 
        total += price * qty
    
    # 4. Call Logic
    # We pass the simple string 'loyalty_tier' directly
    return calculate_final_price.invoke({"cart_total": total, "loyalty_tier": loyalty_tier})

# --- Payment Tools ---
@tool
def process_card_payment(card_number: str, expiry: str, cvv: str, amount: float = 0):
    """Processes a credit/debit card transaction."""
    return f"✅ Transaction Successful! Card ending in {card_number[-4:]} charged. Auth: TXN-7782"

@tool
def generate_upi_qr(amount: float):
    """
    Generates a UPI QR code string for the frontend to render.
    """
    # This specific format triggers the QR component in React
    return f"||QR_CODE:{amount}||"

@tool
def open_secure_payment_form():
    """
    Opens a secure credit card entry form on the user's screen.
    Use this when the user wants to pay by Card.
    """
    # This specific format triggers the Form component in React
    return "||CC_FORM||"

# --- Post Purchase Tools ---
@tool
def get_order_status(fulfillment_id: str):
    """Gets order tracking info."""
    return "Order is Out for Delivery."

@tool
def query_rag_tool_doc(query: str):
    """Queries policy documents."""
    return search_return_policy.invoke({"query": query})

@tool
def process_refund(payment_intent_id: str, reason: str):
    """Processes a refund."""
    return "Refund Initiated."

@tool
def create_fulfillment_order(order_id: str, customer_id: str, items: str):
    """Creates fulfillment record."""
    return "Fulfillment Created."

@tool
def schedule_home_delivery(fulfillment_id: str, address: str):
    """Schedules home delivery."""
    return f"Delivery Scheduled for {fulfillment_id}"

@tool
def schedule_instore_pickup(fulfillment_id: str, store_id: str, slot: str):
    """Schedules store pickup."""
    return f"Pickup Confirmed at {store_id}"

@tool
def request_human_assistance(issue_summary: str):
    """Escalates to human."""
    return "Human Notified."

# --- 3. WORKER NODE FACTORY ---
def create_worker_node(prompt, tools_list, agent_name):
    worker_llm = llm.bind_tools(tools_list)
    
    def worker_node(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=prompt)] + messages
        
        response = worker_llm.invoke(messages)
        
        return {
            "messages": [response],
            "sender": agent_name
        }
    
    return worker_node





import json
import os
from datetime import datetime
from src.config import DATA_DIR

# --- HELPER: Invoice Storage ---
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.json")

def save_invoice_to_db(invoice_data):
    try:
        if not os.path.exists(INVOICE_FILE):
            with open(INVOICE_FILE, "w") as f: json.dump({"invoices": []}, f)
            
        with open(INVOICE_FILE, "r") as f:
            db = json.load(f)
            
        db["invoices"].append(invoice_data)
        
        with open(INVOICE_FILE, "w") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Invoice Save Error: {e}")

# --- NEW TOOL ---
@tool
def generate_invoice(order_id: str, customer_id: str, amount: float, items_summary: str):
    """
    Generates an invoice, saves it to the backend, and returns data for the frontend.
    Args:
        order_id: The ID of the order (e.g. ORD-123)
        customer_id: The user's ID (e.g. CUST001)
        amount: Total amount paid.
        items_summary: Short description of items (e.g. "2x Jeans, 1x Top")
    """
    invoice_data = {
        "invoice_id": f"INV-{int(datetime.now().timestamp())}",
        "order_id": order_id,
        "customer_id": customer_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "items": items_summary,
        "status": "Paid"
    }
    
    # 1. Save to Backend File
    save_invoice_to_db(invoice_data)
    
    # 2. Return Data Tag for Frontend
    return f"||INVOICE_DATA:{json.dumps(invoice_data)}||"

# --- 4. CREATE THE AGENT NODES ---

recommendation_node = create_worker_node(recommendation_prompt, [
    get_customer_profile, find_products, search_products, get_product_details_for_comparison, get_cross_sell_products, check_inventory_status, add_to_cart
], "RecommendationAgent")

inventory_node = create_worker_node(inventory_prompt, [
    check_inventory_status, request_back_in_stock_notification, update_inventory_stock, add_to_cart
], "InventoryAgent")

loyalty_node = create_worker_node(loyalty_prompt, [
    add_to_cart, calculate_final_pricing, get_active_promotions
], "LoyaltyAndOffersAgent")

payment_node = create_worker_node(payment_prompt, [
    process_card_payment, generate_upi_qr ,open_secure_payment_form , generate_invoice
], "PaymentAgent")

fulfillment_node = create_worker_node(fulfillment_prompt, [
    create_fulfillment_order, schedule_home_delivery, schedule_instore_pickup ,generate_invoice
], "FulfillmentAgent")

post_purchase_node = create_worker_node(post_prompt, [
    get_order_status, query_rag_tool_doc, process_refund, request_human_assistance , generate_invoice 
], "PostPurchaseSupportAgent")