import json
import datetime

# ==========================================
# 1. LOYALTY RULES DATA
# ==========================================
loyalty_data = {
    "LOYALTY_TIER_RATES": {
        "Bronze": 0.0,
        "Silver": 0.05,
        "Gold": 0.10,
        "Diamond": 0.15
    },
    "COUPONS": {
        "FOOTWEAR20": {
            "type": "percentage",
            "value": 0.20,
            "applies_to": {"category": "Footwear"},
            "description": "20% Off Footwear"
        }
    },
    "SPECIAL_PROMOTIONS": {
        "BIRTHDAY": {
            "type": "flat",
            "value": 500.00,
            "description": "Birthday Special Flat ₹500 Off!"
        }
    },
    "THRESHOLD_PROMOTIONS": [
        {"threshold": 1000.00, "type": "flat_discount", "value": 200.00, "description": "Flat ₹200 Off on Orders Above ₹1000"},
        {"threshold": 3000.00, "type": "flat_discount", "value": 500.00, "description": "Flat ₹500 Off on Orders Above ₹3000"}
    ]
}

# ==========================================
# 2. INVENTORY DATA
# ==========================================
# Note: I've converted datetime objects to ISO format strings for JSON compatibility
current_time = datetime.datetime.utcnow().isoformat() + "Z"

inventory_data = {
    "1": { "product_sku": "1", "online_stock": 12, "store_locations": [ {"store_id": "DEL-R01", "store_name": "Forever 21 – DLF Saket", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-R02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "2": { "product_sku": "2", "online_stock": 8, "store_locations": [ {"store_id": "DEL-R03", "store_name": "TASVA – South Extension I", "stock_count": 4, "click_and_collect_enabled": True}, {"store_id": "DEL-R04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "3": { "product_sku": "3", "online_stock": 15, "store_locations": [ {"store_id": "DEL-R05", "store_name": "Van Heusen – Connaught Place", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-R01", "store_name": "Forever 21 – DLF Saket", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "4": { "product_sku": "4", "online_stock": 10, "store_locations": [ {"store_id": "DEL-R02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 4, "click_and_collect_enabled": True}, {"store_id": "DEL-R03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "5": { "product_sku": "5", "online_stock": 7, "store_locations": [ {"store_id": "DEL-R04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-R05", "store_name": "Van Heusen – Connaught Place", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "6": { "product_sku": "6", "online_stock": 18, "store_locations": [ {"store_id": "DEL-R01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-R02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "7": { "product_sku": "7", "online_stock": 14, "store_locations": [ {"store_id": "DEL-R03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-R04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "8": { "product_sku": "8", "online_stock": 9, "store_locations": [ {"store_id": "DEL-R05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-R01", "store_name": "Forever 21 – DLF Saket", "stock_count": 4, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "9": { "product_sku": "9", "online_stock": 6, "store_locations": [ {"store_id": "DEL-R02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-R03", "store_name": "TASVA – South Extension I", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "10": { "product_sku": "10", "online_stock": 11, "store_locations": [ {"store_id": "DEL-R04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-R05", "store_name": "Van Heusen – Connaught Place", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "101": { "product_sku": "101", "online_stock": 10, "store_locations": [ {"store_id": "DEL-J01", "store_name": "Forever 21 – DLF Saket", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-J02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "102": { "product_sku": "102", "online_stock": 14, "store_locations": [ {"store_id": "DEL-J03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-J04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "103": { "product_sku": "103", "online_stock": 8, "store_locations": [ {"store_id": "DEL-J05", "store_name": "Van Heusen – Connaught Place", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-J01", "store_name": "Forever 21 – DLF Saket", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "104": { "product_sku": "104", "online_stock": 12, "store_locations": [ {"store_id": "DEL-J02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-J03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "105": { "product_sku": "105", "online_stock": 17, "store_locations": [ {"store_id": "DEL-J04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-J05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "201": { "product_sku": "201", "online_stock": 9, "store_locations": [ {"store_id": "DEL-S01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-S02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "202": { "product_sku": "202", "online_stock": 15, "store_locations": [ {"store_id": "DEL-S03", "store_name": "TASVA – South Extension I", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-S04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "203": { "product_sku": "203", "online_stock": 7, "store_locations": [ {"store_id": "DEL-S05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-S01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "204": { "product_sku": "204", "online_stock": 12, "store_locations": [ {"store_id": "DEL-S02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-S03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "205": { "product_sku": "205", "online_stock": 18, "store_locations": [ {"store_id": "DEL-S04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-S05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "206": { "product_sku": "206", "online_stock": 13, "store_locations": [ {"store_id": "DEL-S01", "store_name": "Forever 21 – DLF Saket", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-S02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "207": { "product_sku": "207", "online_stock": 6, "store_locations": [ {"store_id": "DEL-S03", "store_name": "TASVA – South Extension I", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-S04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "208": { "product_sku": "208", "online_stock": 11, "store_locations": [ {"store_id": "DEL-S05", "store_name": "Van Heusen – Connaught Place", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-S01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "301": { "product_sku": "301", "online_stock": 8, "store_locations": [ {"store_id": "DEL-B01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-B02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "302": { "product_sku": "302", "online_stock": 15, "store_locations": [ {"store_id": "DEL-B03", "store_name": "TASVA – South Extension I", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-B04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "303": { "product_sku": "303", "online_stock": 12, "store_locations": [ {"store_id": "DEL-B05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-B01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "304": { "product_sku": "304", "online_stock": 7, "store_locations": [ {"store_id": "DEL-B02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-B03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "305": { "product_sku": "305", "online_stock": 14, "store_locations": [ {"store_id": "DEL-B04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 3, "click_and_collect_enabled": True}, {"store_id": "DEL-B05", "store_name": "Van Heusen – Connaught Place", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "306": { "product_sku": "306", "online_stock": 10, "store_locations": [ {"store_id": "DEL-B01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-B02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "307": { "product_sku": "307", "online_stock": 16, "store_locations": [ {"store_id": "DEL-B03", "store_name": "TASVA – South Extension I", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-B04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "308": { "product_sku": "308", "online_stock": 9, "store_locations": [ {"store_id": "DEL-B05", "store_name": "Van Heusen – Connaught Place", "stock_count": 1, "click_and_collect_enabled": True}, {"store_id": "DEL-B01", "store_name": "Forever 21 – DLF Saket", "stock_count": 2, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "309": { "product_sku": "309", "online_stock": 11, "store_locations": [ {"store_id": "DEL-B02", "store_name": "Jaypore – Dwarka Vegas Mall", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-B03", "store_name": "TASVA – South Extension I", "stock_count": 1, "click_and_collect_enabled": True} ], "last_updated": current_time },
    "310": { "product_sku": "310", "online_stock": 13, "store_locations": [ {"store_id": "DEL-B04", "store_name": "Pantaloons – Pacific Mall Tagore Garden", "stock_count": 2, "click_and_collect_enabled": True}, {"store_id": "DEL-B05", "store_name": "Van Heusen – Connaught Place", "stock_count": 3, "click_and_collect_enabled": True} ], "last_updated": current_time }
}

# Write files
with open("loyalty_rules.json", "w") as f:
    json.dump(loyalty_data, f, indent=4)
    print("✅ Created loyalty_rules.json")

with open("inventory.json", "w") as f:
    json.dump(inventory_data, f, indent=4)
    print("✅ Created inventory.json")