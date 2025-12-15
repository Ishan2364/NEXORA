import os
import json
from typing import Union
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from datetime import datetime
from src.graph.state import AgentState
from src.config import DATA_DIR
import uuid

# --- IMPORT BASE TOOLS (To make them available for workflow.py) ---
from src.tools.catalog_tools import search_catalog
from src.tools.loyalty_tools import calculate_final_price
from src.tools.inventory_tools import check_inventory_status as real_check_inventory
from src.tools.crm_tools import get_customer_profile as real_get_profile
from src.tools.policy_tools import search_return_policy

# --- 1. SETUP ENV ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Check your .env file.")

# Using Instant model for speed/stability
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY, temperature=0)

# --- 2. HELPER FUNCTIONS ---
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")

def save_invoice_to_db(invoice_data):
    """Saves invoice to persistent JSON file with forced flushing."""
    try:
        # 1. Initialize file if missing
        if not os.path.exists(INVOICE_FILE):
            with open(INVOICE_FILE, "w", encoding='utf-8') as f:
                json.dump({"invoices": []}, f)
            print(f"📁 Created new invoice file at {INVOICE_FILE}")

        # 2. Read existing data
        with open(INVOICE_FILE, "r", encoding='utf-8') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = {"invoices": []} # Handle corrupt/empty file

        # 3. Check for duplicates
        existing_ids = {inv.get('invoice_id') for inv in db.get("invoices", [])}
        
        if invoice_data['invoice_id'] not in existing_ids:
            # 4. Append and Save
            db["invoices"].append(invoice_data)
            
            with open(INVOICE_FILE, "w", encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
                f.flush() # Force write to disk
                os.fsync(f.fileno()) # Double force for OS level
            
            print(f"✅ PERMANENTLY SAVED INVOICE: {invoice_data['invoice_id']}")
        else:
            print(f"⚠️ Duplicate invoice detected, skipped save.")

    except Exception as e:
        print(f"❌ CRITICAL SAVE ERROR: {str(e)}")

def update_customer_history(customer_id, invoice_data):
    """Updates customer purchase history in JSON file."""
    try:
        if not os.path.exists(CUSTOMERS_FILE): 
            print("❌ CUSTOMERS FILE NOT FOUND")
            return

        with open(CUSTOMERS_FILE, "r") as f:
            data = json.load(f)
        
        customer_found = False
        for cust in data["customers"]:
            if cust["customer_id"] == customer_id:
                # Create new order object matching your format
                new_order = {
                    "date": invoice_data["date"],
                    "category": "Apparel", # Default category
                    "product": invoice_data["items"], # Summary from invoice
                    "sku_type": "Apparel", # Required field
                    "quantity": 1,
                    "price": float(invoice_data["amount"]),
                    "channel": "Web",
                    "payment_method": "Online",
                    "returned": False
                }
                
                # Ensure list exists
                if "purchase_history" not in cust: cust["purchase_history"] = []
                
                # Add to TOP of list
                cust["purchase_history"].insert(0, new_order)
                customer_found = True
                break
        
        if customer_found:
            with open(CUSTOMERS_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"✅ UPDATED HISTORY FOR: {customer_id}")
        else:
            print(f"❌ CUSTOMER NOT FOUND: {customer_id}")
            
    except Exception as e:
        print(f"❌ HISTORY UPDATE ERROR: {e}")

# --- 3. DEFINE TOOLS ---

from langchain_core.runnables import RunnableConfig

@tool

def generate_invoice(order_id: str, customer_id: str, amount: float, items_summary: str):

    """

    Generates an invoice, saves it to the backend, and returns data for the frontend.

    """

    # Create the timestamped ID once here to ensure consistency

    inv_id = f"INV-{int(datetime.now().timestamp())}"

    print(f"🧾 Generating Invoice ID: {inv_id}")

    print(f"🧾 Order ID: {order_id}, Customer ID: {customer_id}, Amount: {amount}")

    invoice_data = {

        "invoice_id": inv_id,

        "order_id": order_id,

        "customer_id": customer_id,

        "date": datetime.now().strftime("%Y-%m-%d"),

        "amount": amount,

        "items": items_summary,

        "status": "Paid"

    }

   

    # 1. Force Save to Invoices File

    save_invoice_to_db(invoice_data)



    # 2. Force Update Customer History

    update_customer_history(customer_id, invoice_data)

   

    return f"||INVOICE_DATA:{json.dumps(invoice_data)}||"


@tool
def add_to_cart(product_sku: str, quantity: int = 1):
    """Adds a specific product SKU to the customer's shopping cart."""
    return json.dumps({"status": "success", "message": f"Added {quantity}x {product_sku}", "sku": product_sku})

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
def check_inventory_status(product_sku: str):
    """Checks stock."""
    return real_check_inventory.invoke({"product_sku": product_sku})

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

@tool
def get_customer_profile(customer_id: str):
    """Fetches customer profile."""
    return real_get_profile.invoke({"customer_id": customer_id})

@tool
def calculate_final_pricing(cart_items: Union[list, str], loyalty_tier: str = "Bronze", coupon_codes: Union[list, str] = None):
    """Calculates final price."""
    if isinstance(cart_items, str):
        try: cart_items = json.loads(cart_items)
        except: cart_items = []
    
    total = len(cart_items) * 2000 if cart_items else 2000 # Dummy logic for safety
    return calculate_final_price.invoke({"cart_total": total, "loyalty_tier": loyalty_tier})

@tool
def process_card_payment(card_number: str, expiry: str, cvv: str, amount: float = 0):
    """Processes a credit/debit card transaction."""
    return f"✅ Transaction Successful! Auth: TXN-{int(datetime.now().timestamp())}"

@tool
def generate_upi_qr(amount: float):
    """Generates a UPI QR code string."""
    return f"||QR_CODE:{amount}||"

@tool
def open_secure_payment_form():
    """Opens a secure credit card entry form."""
    return "||CC_FORM||"

@tool
def get_order_status(fulfillment_id: str):
    """Gets order tracking info."""
    return "Order is Out for Delivery."

# 1. Import the tool from the file you just created
from src.tools.policy_tools import search_return_policy

# 2. Define the Agent Tool that wraps it
@tool
def query_rag_tool_doc(query: str):
    """
    Consults the official policy documents to answer user questions 
    about returns, refunds, shipping, or conditions.
    """
    # The agent passes the user's question (e.g., "Can I return heels?")
    # The tool searches the PDF vector store
    return search_return_policy.invoke(query)

@tool
def process_refund(payment_intent_id: str, reason: str):
    """Processes a refund."""
    return "Refund Initiated."

@tool
def create_fulfillment_order(order_id: str = None, customer_id: str = None, items: str = ""):
    """Creates fulfillment record."""
    return f"Fulfillment Created."

@tool
def schedule_home_delivery(address: str = "Default Address"):
    """Schedules home delivery."""
    return f"Delivery Scheduled to {address}"

@tool
def schedule_instore_pickup(store_id: str):
    """Schedules store pickup."""
    return f"Pickup Confirmed at {store_id}"

@tool
def request_human_assistance(issue_summary: str):
    """Escalates to human."""
    return "Human Notified."

# --- 4. CREATE WORKER NODE FACTORY ---
# --- 4. WORKER NODE FACTORY (UPDATED FOR ID FIX) ---
def create_worker_node(prompt, tools_list, agent_name):
    worker_llm = llm.bind_tools(tools_list)
    
    def worker_node(state: AgentState):
        messages = state["messages"]
        
        # --- LOGIC UPDATE START ---
        # 1. SCAN HISTORY: Look through all messages for a "CUST..." pattern
        found_id = None
        for m in messages:
            # Handle different message types safely
            content = m.content if hasattr(m, 'content') else str(m)
            
            # Regex to find 'CUST' followed by digits (e.g., CUST020, CUST001)
            import re
            match = re.search(r"(CUST\d+)", content)
            if match:
                found_id = match.group(1)
                break # Stop as soon as we find the first valid ID (usually from login)
        
        # 2. CREATE CONTEXT: Build the strict instruction string
        user_context = ""
        if found_id:
            user_context = f"\n\n🚨 CRITICAL SYSTEM INSTRUCTION: The authenticated Customer ID is '{found_id}'. You MUST use '{found_id}' for all tool calls. DO NOT invent 'CUST123' or any other ID."
        else:
            # Fallback if the history was completely wiped or empty
            user_context = "\n\n🚨 WARNING: No Customer ID found in history. If a tool needs an ID, ask the user for it."

        # 3. INJECT: Add this context to the system prompt
        final_prompt = prompt + user_context
        
        # 4. PREPARE MESSAGES: Ensure the new System Message is first
        # Filter out old system messages to avoid confusion
        filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
        final_messages = [SystemMessage(content=final_prompt)] + filtered_messages
        
        # --- LOGIC UPDATE END ---
        
        response = worker_llm.invoke(final_messages)
        
        return {
            "messages": [response],
            "sender": agent_name
        }
    
    return worker_node

# --- 5. EXPORT NODES ---
from src.agents.prompts import (
    recommendation_prompt, inventory_prompt, loyalty_prompt, 
    payment_prompt, fulfillment_prompt, post_prompt
)

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
    process_card_payment, generate_upi_qr, open_secure_payment_form
    # NOTE: generate_invoice is EXCLUDED here to enforce the prompt rule
], "PaymentAgent")

fulfillment_node = create_worker_node(fulfillment_prompt, [
    create_fulfillment_order, schedule_home_delivery, schedule_instore_pickup, generate_invoice
], "FulfillmentAgent")

post_purchase_node = create_worker_node(post_prompt, [
    get_order_status, query_rag_tool_doc, process_refund, request_human_assistance 
], "PostPurchaseSupportAgent")