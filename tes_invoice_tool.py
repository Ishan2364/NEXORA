import sys
import os
import json
import time

# --- 1. SETUP PATHS ---
# Ensure we can import from 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'src'))

# Import the specific functions to test
try:
    from src.agents.worker_agents import generate_invoice
    from src.config import DATA_DIR
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("Make sure you are running this script from the root folder (abfrl_retail_agent).")
    sys.exit(1)

# Define file paths for verification
INVOICES_FILE = os.path.join(DATA_DIR, "invoices.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")

def test_generate_invoice():
    print("\n------------------------------------------------------------")
    print("🧪 STARTING TEST: generate_invoice Tool")
    print("------------------------------------------------------------")

    # --- 2. PREPARE TEST DATA ---
    test_order_id = f"TEST-ORD-{int(time.time())}"
    test_customer_id = "CUST020"  # Ensure this ID exists in your customers.json for the history update test
    test_amount = 9999.00
    test_items = "1x Test Python Script Item"

    print(f"🔹 Input Data:")
    print(f"   - Order ID: {test_order_id}")
    print(f"   - Customer ID: {test_customer_id}")
    print(f"   - Amount: {test_amount}")

    # --- 3. CALL THE TOOL DIRECTLY ---
    print("\n🔹 Calling tool...")
    try:
        # We invoke the tool just like the agent would
        result = generate_invoice.invoke({
            "order_id": test_order_id,
            "customer_id": test_customer_id,
            "amount": test_amount,
            "items_summary": test_items
        })
        print(f"✅ Tool returned successfully:\n   {result}")
    except Exception as e:
        print(f"❌ TOOL CRASHED: {e}")
        return

    # --- 4. VERIFY 'invoices.json' ---
    print("\n🔹 Verifying 'invoices.json'...")
    try:
        if not os.path.exists(INVOICES_FILE):
            print("❌ FAIL: invoices.json does not exist!")
        else:
            with open(INVOICES_FILE, "r") as f:
                inv_db = json.load(f)
            
            # Search for our unique test order ID
            found_invoice = next((inv for inv in inv_db.get("invoices", []) if inv["order_id"] == test_order_id), None)
            
            if found_invoice:
                print(f"✅ SUCCESS: Invoice found in file!")
                print(f"   - Invoice ID: {found_invoice.get('invoice_id')}")
            else:
                print("❌ FAIL: Tool finished, but data NOT found in invoices.json")
    except Exception as e:
        print(f"❌ READ ERROR: {e}")

    # --- 5. VERIFY 'customers.json' ---
    print("\n🔹 Verifying 'customers.json' (Purchase History)...")
    try:
        if not os.path.exists(CUSTOMERS_FILE):
            print("❌ FAIL: customers.json does not exist!")
        else:
            with open(CUSTOMERS_FILE, "r") as f:
                cust_db = json.load(f)
            
            # Find the customer
            customer = next((c for c in cust_db.get("customers", []) if c["customer_id"] == test_customer_id), None)
            
            if customer:
                # Check their latest order
                history = customer.get("purchase_history", [])
                if not history:
                     print("❌ FAIL: Customer found, but history is empty.")
                else:
                    latest_order = history[0]
                    # Check if it matches our test data (price is a good unique check)
                    if latest_order.get("price") == test_amount:
                         print(f"✅ SUCCESS: History updated for {test_customer_id}!")
                         print(f"   - Latest Item: {latest_order.get('product')}")
                    else:
                         print(f"❌ FAIL: History exists, but latest order doesn't match test data.")
                         print(f"   - Found Price: {latest_order.get('price')}, Expected: {test_amount}")
            else:
                print(f"⚠️ SKIP: Customer {test_customer_id} not found in file. Create this customer to test history update.")

    except Exception as e:
        print(f"❌ READ ERROR: {e}")

    print("\n------------------------------------------------------------")
    print("🏁 TEST COMPLETE")
    print("------------------------------------------------------------")

if __name__ == "__main__":
    test_generate_invoice()