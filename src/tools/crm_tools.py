import json
from langchain_core.tools import tool
from src.config import CUSTOMERS_FILE

@tool
def get_customer_profile(customer_id: str):
    """
    Retrieves the customer profile (loyalty tier, history, preferences) by Customer ID.
    Use this when a user identifies themselves (e.g., 'I am CUST001').
    """
    try:
        with open(CUSTOMERS_FILE, "r") as f:
            data = json.load(f)
            
        # Handle the format provided in your uploaded file
        customers = data.get("customers", [])
        for cust in customers:
            if cust["customer_id"] == customer_id:
                return cust
        return {"error": "Customer not found."}
    except Exception as e:
        return {"error": f"Failed to load customer DB: {str(e)}"}