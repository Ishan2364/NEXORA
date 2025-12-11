import json
from langchain_core.tools import tool
from src.config import INVENTORY_FILE

# Renamed to match your 'inventory_prompt'
@tool
def check_inventory_status(product_sku: str):
    """
    Checks real-time stock availability. 
    Returns JSON with online_stock and store_locations.
    """
    try:
        with open(INVENTORY_FILE, "r") as f:
            data = json.load(f)
        product = data.get(product_sku)
        if not product:
            return json.dumps({"error": "SKU not found", "online_stock": 0, "store_locations": []})
        return json.dumps({
            "online_stock": product.get("online_stock", 0),
            "store_locations": product.get("store_locations", [])
        })
    except Exception as e:
        return json.dumps({"error": str(e)})