import os
import json
from typing import Union
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from src.graph.state import AgentState
from src.config import DATA_DIR
import uuid
from typing import Union, Optional
from langchain_core.runnables import RunnableConfig 

# ... (Keep all your tools and imports above) ...

# --- 4. ROBUST WORKER NODE FACTORY ---
def create_worker_node(prompt, tools_list, agent_name):
    worker_llm = llm.bind_tools(tools_list)
    
    # We update the signature to accept 'config'
    def worker_node(state: AgentState, config: RunnableConfig):
        messages = state["messages"]
        found_id = None
        
        # STRATEGY 1: Get ID from the Session/Thread ID (Most Reliable)
        # Your session_id is likely "CUST005-17234..."
        try:
            thread_id = config.get("configurable", {}).get("thread_id", "")
            import re
            match = re.search(r"(CUST\d+)", str(thread_id))
            if match:
                found_id = match.group(1)
                # print(f"🆔 DEBUG: Found Customer ID in Session: {found_id}")
        except:
            pass

        # STRATEGY 2: Scan Chat History (Fallback)
        if not found_id:
            for m in messages:
                content = m.content if hasattr(m, 'content') else str(m)
                match = re.search(r"(CUST\d+)", content)
                if match:
                    found_id = match.group(1)
                    break
        
        # Create the strict context injection
        user_context = ""
        if found_id:
            user_context = (
                f"\n\n🚨 SYSTEM CONTEXT: The authenticated Customer ID is '{found_id}'. "
                f"You MUST use '{found_id}' for all tool calls (like view_cart, add_to_cart). "
                f"Do NOT ask the user for their ID."
            )
        else:
            user_context = "\n\n🚨 WARNING: No Customer ID found in session. If needed, ask the user."

        # Inject into prompt
        final_prompt = prompt + user_context
        
        # Filter messages and invoke
        filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
        final_messages = [SystemMessage(content=final_prompt)] + filtered_messages
        
        response = worker_llm.invoke(final_messages)
        
        return {
            "messages": [response],
            "sender": agent_name
        }
    
    return worker_node
# --- IMPORT BASE TOOLS ---
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

# --- 2. HELPER FUNCTIONS (DB & FILE IO) ---
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
CONTEXT_FILE = os.path.join(DATA_DIR, "user_context.json")
CARTS_FILE = os.path.join(DATA_DIR, "carts.json")


# --- CART HELPER FUNCTIONS ---
def load_cart_db():
    if not os.path.exists(CARTS_FILE):
        return {}
    try:
        with open(CARTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_cart_db(data):
    with open(CARTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_context_db():
    if not os.path.exists(CONTEXT_FILE):
        return {}
    try:
        with open(CONTEXT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_context_db(data):
    with open(CONTEXT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_invoice_to_db(invoice_data):
    """Saves invoice to persistent JSON file with forced flushing."""
    try:
        if not os.path.exists(INVOICE_FILE):
            with open(INVOICE_FILE, "w", encoding='utf-8') as f:
                json.dump({"invoices": []}, f)
        
        with open(INVOICE_FILE, "r", encoding='utf-8') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = {"invoices": []}

        existing_ids = {inv.get('invoice_id') for inv in db.get("invoices", [])}
        
        if invoice_data['invoice_id'] not in existing_ids:
            db["invoices"].append(invoice_data)
            with open(INVOICE_FILE, "w", encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
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
                new_order = {
                    "date": invoice_data["date"],
                    "category": "Apparel",
                    "product": invoice_data["items"],
                    "sku_type": "Apparel",
                    "quantity": 1,
                    "price": float(invoice_data["amount"]),
                    "channel": "Web",
                    "payment_method": "Online",
                    "returned": False
                }
                if "purchase_history" not in cust: cust["purchase_history"] = []
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
@tool
def add_to_cart(customer_id: str, product_sku: str, product_name: str, price: float, quantity: int = 1):
    """
    Adds a product to the cart and ensures Loyalty Tier is saved.
    """
    print(f"🛒 TOOL CALLED: Adding {product_name} ({product_sku}) to {customer_id}")
    
    db = load_cart_db()
    
    # 1. Ensure Customer Record Exists
    if customer_id not in db:
        db[customer_id] = {
            "customer_id": customer_id,
            "items": [], 
            "total": 0
        }

    # 2. CRITICAL FIX: If Tier is missing or None, Fetch it NOW (Even for existing carts)
    if db[customer_id].get("loyalty_tier") is None:
        print(f"🔍 Tier missing for {customer_id}. Fetching from Profile...")
        tier = "Bronze" # Default
        try:
            profile_data = real_get_profile.invoke({"customer_id": customer_id})
            profile_str = str(profile_data)
            
            import re
            if re.search(r"Platinum", profile_str, re.IGNORECASE):
                tier = "Platinum"
            elif re.search(r"Diamond", profile_str, re.IGNORECASE):
                tier = "Diamond"
            elif re.search(r"Gold", profile_str, re.IGNORECASE):
                tier = "Gold"
            elif re.search(r"Silver", profile_str, re.IGNORECASE):
                tier = "Silver"
            
            print(f"💎 DETECTED TIER: {tier}")
        except Exception as e:
            print(f"⚠️ Tier detection failed: {e}. Defaulting to Bronze.")
        
        # Save the found tier to the DB object
        db[customer_id]["loyalty_tier"] = tier

    # 3. Add/Update Item
    item_found = False
    for item in db[customer_id]["items"]:
        if item["sku"] == product_sku:
            item["quantity"] += quantity
            item_found = True
            break
    
    if not item_found:
        db[customer_id]["items"].append({
            "sku": product_sku,
            "name": product_name,
            "price": price,
            "quantity": quantity
        })
    
    # 4. Recalculate Total
    new_total = sum(item["price"] * item["quantity"] for item in db[customer_id]["items"])
    db[customer_id]["total"] = new_total
    
    save_cart_db(db)
    print(f"✅ SAVED TO CARTS.JSON: {product_name} (Tier: {db[customer_id].get('loyalty_tier')})")
    return json.dumps({"status": "success", "message": f"Added {product_name}. Total: ₹{new_total}"})

@tool
def view_cart(customer_id: str):
    """Retrieves cart contents, total price, and LOYALTY TIER."""
    db = load_cart_db()
    cart = db.get(customer_id)
    
    if not cart or not cart["items"]:
        return "The cart is currently empty."
    
    # CHANGE: We now explicitly include the Tier in the summary string
    tier = cart.get("loyalty_tier", "Bronze")
    summary = f"🛒 **Current Cart (Tier: {tier}):**\n"
    
    for item in cart["items"]:
        name = item.get('name', 'Unknown Item')
        summary += f"- {name} (SKU: {item['sku']}) x{item['quantity']} | ₹{item['price'] * item['quantity']}\n"
    
    summary += f"\n**Total Amount:** ₹{cart['total']}"
    return summary

@tool
def clear_cart(customer_id: str):
    """Empty the cart but keep the user's metadata (Tier)."""
    db = load_cart_db()
    if customer_id in db:
        # Preserve the Tier!
        current_tier = db[customer_id].get("loyalty_tier", "Bronze")
        
        db[customer_id] = {
            "customer_id": customer_id, 
            "items": [], 
            "total": 0,
            "loyalty_tier": current_tier # <--- KEEP TIER
        }
        save_cart_db(db)
    return "Cart cleared."

# --- GENERATE INVOICE (No Logic Change needed, just behavior) ---
@tool
def generate_invoice(order_id: str, customer_id: str, amount: float, items_summary: str):
    """
    Generates an invoice.
    'items_summary' should be a descriptive string like: "Red Saree (SKU-101), Blue Jeans (SKU-102)"
    """
    inv_id = f"INV-{int(datetime.now().timestamp())}"
    
    # 1. Create Data
    invoice_data = {
        "invoice_id": inv_id,
        "order_id": order_id,
        "customer_id": customer_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "items": items_summary, # This will now contain names because view_cart provides them!
        "status": "Paid"
    }
    
    # 2. Save
    save_invoice_to_db(invoice_data)
    update_customer_history(customer_id, invoice_data)
    
    return f"||INVOICE_DATA:{json.dumps(invoice_data)}||"

# --- UPDATED SEARCH TOOLS ---

@tool
def find_products(
    gender: Optional[str] = None, 
    category: Optional[str] = None, 
    sub_category: Optional[str] = None, 
    max_price: Optional[float] = None
):
    """
    Smart search for products. 
    Can filter by gender, category (e.g., 'Clothing'), or sub_category (e.g., 'Dresses').
    """
    # Build a natural language query from the filters
    query_parts = []
    if gender: query_parts.append(gender)
    if category: query_parts.append(category)
    if sub_category: query_parts.append(sub_category)
    
    search_query = " ".join(query_parts)
    
    # We use the robust search_catalog tool we just built
    return search_catalog.invoke({"query": search_query})

@tool
def search_products(query: str):
    """Free text search (e.g., 'Red party dress', 'Black heels')."""
    return search_catalog.invoke({"query": query})

@tool
def get_product_details_for_comparison(product_ids: list):
    """Fetches details for specific SKUs."""
    # We just search for the SKUs or Names
    return search_catalog.invoke({"query": " ".join(product_ids)})

@tool
def get_cross_sell_products(product_id: str):
    """
    Recommends matching items.
    Logic: If buying a Dress (SKU 1-10, 301+), recommend Heels/Jackets.
    """
    # Simple logic: If it's a dress, suggest heels. If heels, suggest jackets.
    # In a real app, this would use the 'category' field dynamically.
    return search_catalog.invoke({"query": "Heels Jackets Accessories"})

@tool
def check_inventory_status(product_sku: str):
    """
    Checks stock. 
    Since the new data focuses on sales_count, we assume items are In Stock.
    """
    return json.dumps({
        "sku": product_sku, 
        "status": "In Stock", 
        "message": "Available for immediate dispatch."
    })

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
def calculate_final_pricing(
    cart_items: Optional[Union[list, str]] = None, 
    customer_id: Optional[str] = None, 
    loyalty_tier: Optional[str] = None, 
    coupon_codes: Union[list, str] = None
):
    """
    Calculates final price. 
    CRITICAL: You MUST provide 'customer_id' to read the real cart total.
    CRITICAL: You MUST provide 'loyalty_tier' (do not guess).
    """
    total_amount = 0.0
    
    # 1. Try to get total from Persistent Cart (carts.json) - This is the BEST way
    if customer_id:
        db = load_cart_db()
        if customer_id in db:
            total_amount = float(db[customer_id].get("total", 0))
            if total_amount > 0:
                print(f"💰 CALC PRICING: Found accurate total for {customer_id}: ₹{total_amount}")

    # 2. Fallback: If no DB total, try to calculate from the list provided by LLM
    if total_amount == 0 and cart_items:
        if isinstance(cart_items, str):
            try: cart_items = json.loads(cart_items)
            except: cart_items = []
        
        # Sum up Price * Quantity
        for item in cart_items:
            p = item.get("price")
            q = item.get("quantity", 1)
            
            if p is not None:
                total_amount += (float(p) * int(q))
            else:
                print(f"❌ PRICING WARNING: Item {item.get('sku', '?')} has NO PRICE. Skipping.")

    # 3. ERRORS: If we still don't have a total or tier, FAIL loudly in terminal
    if total_amount == 0:
        print("❌ PRICING FAILURE: Cart is empty or prices are missing. Cannot calculate.")
        return "Error: The cart total is 0. Please ensure items with prices are added to the cart."

    if not loyalty_tier:
        print("❌ PRICING FAILURE: Agent did not provide Loyalty Tier.")
        return "Error: I cannot calculate the price without the user's Loyalty Tier. Please check their profile."

    # 4. Run the calculation engine with REAL data
    return calculate_final_price.invoke({"cart_total": total_amount, "loyalty_tier": loyalty_tier})

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

@tool
def query_rag_tool_doc(query: str):
    """Consults the official policy documents."""
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


# --- CONTEXT MANAGEMENT TOOLS ---
# Note: These strings are internal to the Tools, not the Agent Prompt
SUMMARIZER_PROMPT_TEXT = """
Analyze chat history from {platform}.
GOAL: Create JSON summary for next session.
OUTPUT JSON: {{ "summary": "...", "last_purchased": "...", "pending_actions": [] }}
CHAT HISTORY: {chat_history}
"""
GREETING_PROMPT_TEXT = """
You are 'Nexora', an elite Retail Associate.
User Profile: {user_profile_data}
Current Platform: {current_platform}
Last Context ({last_platform}): {summary}

**TASK:**
Generate a warm, short (1-2 sentences) greeting.
1. **IDENTIFY NAME:** Look at the 'User Profile' above and use the user's **REAL FIRST NAME** (e.g., "Ayesha", "Ishan"). 
2. **FORBIDDEN:** Do NOT call them by their ID (e.g., "CUST005").
3. **CONTEXT:** Reference their last activity naturally to show continuity.

**Greeting:**
"""

@tool 
def generate_session_summary(cust_id, platform, chat_history):
    """Called on SIGN OUT to summarize and save session."""
    if not chat_history: return "No history."
    
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    prompt = ChatPromptTemplate.from_template(SUMMARIZER_PROMPT_TEXT)
    chain = prompt | llm 
    
    try:
        response = chain.invoke({"platform": platform, "chat_history": history_text})
        content = response.content.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(content)
    except:
        analysis = {"summary": "User visited previously.", "last_purchased": None}

    db = load_context_db()
    db[cust_id] = {
        "last_platform": platform,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": analysis.get("summary"),
        "last_purchased": analysis.get("last_purchased"),
        "pending_actions": analysis.get("pending_actions", [])
    }
    save_context_db(db)
    return "Context Saved Successfully"

@tool
def generate_welcome_message(cust_id, current_platform):
    """
    Called on LOGIN.
    Fetches User Name + Context to generate a personalized greeting.
    """
    db = load_context_db()
    user_data = db.get(cust_id)

    # 1. Fetch Real Name (The Fix)
    try:
        # We invoke the existing CRM tool to get the full profile string/json
        profile_data = real_get_profile.invoke({"customer_id": cust_id})
    except Exception as e:
        print(f"⚠️ Could not fetch profile for greeting: {e}")
        profile_data = "Name: Valued Customer"

    # 2. Handle New User (No Context history)
    if not user_data:
        # Even for new users, we want to use their Real Name
        prompt = ChatPromptTemplate.from_template(GREETING_PROMPT_TEXT)
        chain = prompt | llm
        response = chain.invoke({
            "user_profile_data": str(profile_data),
            "current_platform": current_platform,
            "last_platform": "None",
            "summary": "First time visitor",
        })
        return response.content

    # 3. Handle Returning User
    prompt = ChatPromptTemplate.from_template(GREETING_PROMPT_TEXT)
    chain = prompt | llm
    response = chain.invoke({
        "user_profile_data": str(profile_data),
        "current_platform": current_platform,
        "last_platform": user_data['last_platform'],
        "summary": user_data['summary']
    })
    
    return response.content

# --- 4. WORKER NODE FACTORY ---
def create_worker_node(prompt, tools_list, agent_name):
    worker_llm = llm.bind_tools(tools_list)
    
    # We update the signature to accept 'config'
    def worker_node(state: AgentState, config: RunnableConfig):
        messages = state["messages"]
        found_id = None
        
        # STRATEGY 1: Get ID from the Session/Thread ID (Most Reliable)
        # Your session_id is likely "CUST005-17234..."
        try:
            thread_id = config.get("configurable", {}).get("thread_id", "")
            import re
            match = re.search(r"(CUST\d+)", str(thread_id))
            if match:
                found_id = match.group(1)
                # print(f"🆔 DEBUG: Found Customer ID in Session: {found_id}")
        except:
            pass

        # STRATEGY 2: Scan Chat History (Fallback)
        if not found_id:
            for m in messages:
                content = m.content if hasattr(m, 'content') else str(m)
                match = re.search(r"(CUST\d+)", content)
                if match:
                    found_id = match.group(1)
                    break
        
        # Create the strict context injection
        user_context = ""
        if found_id:
            user_context = (
                f"\n\n🚨 SYSTEM CONTEXT: The authenticated Customer ID is '{found_id}'. "
                f"You MUST use '{found_id}' for all tool calls (like view_cart, add_to_cart). "
                f"Do NOT ask the user for their ID."
            )
        else:
            user_context = "\n\n🚨 WARNING: No Customer ID found in session. If needed, ask the user."

        # Inject into prompt
        final_prompt = prompt + user_context
        
        # Filter messages and invoke
        filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
        final_messages = [SystemMessage(content=final_prompt)] + filtered_messages
        
        response = worker_llm.invoke(final_messages)
        
        return {
            "messages": [response],
            "sender": agent_name
        }
    
    return worker_node


# --- 5. EXPORT NODES ---
from src.agents.prompts import (
    recommendation_prompt, inventory_prompt, loyalty_prompt, 
    payment_prompt, fulfillment_prompt, post_prompt, 
    context_prompt  # <--- MAKE SURE YOU ADD THIS TO PROMPTS.PY
)

recommendation_node = create_worker_node(recommendation_prompt, [
    view_cart ,get_customer_profile, find_products, search_products, get_product_details_for_comparison, get_cross_sell_products, check_inventory_status, add_to_cart
], "RecommendationAgent")

inventory_node = create_worker_node(inventory_prompt, [
    check_inventory_status, request_back_in_stock_notification, update_inventory_stock, add_to_cart
], "InventoryAgent")

loyalty_node = create_worker_node(loyalty_prompt, [
   view_cart, add_to_cart, calculate_final_pricing, get_active_promotions
], "LoyaltyAndOffersAgent")

payment_node = create_worker_node(payment_prompt, [
   view_cart, process_card_payment, generate_upi_qr, open_secure_payment_form
], "PaymentAgent")

fulfillment_node = create_worker_node(fulfillment_prompt, [
  clear_cart ,view_cart ,  create_fulfillment_order, schedule_home_delivery, schedule_instore_pickup, generate_invoice
], "FulfillmentAgent")

post_purchase_node = create_worker_node(post_prompt, [
    get_order_status, query_rag_tool_doc, process_refund, request_human_assistance 
], "PostPurchaseSupportAgent")

context_manager_node = create_worker_node(context_prompt, [
    generate_session_summary, generate_welcome_message
], "ContextManagerAgent")