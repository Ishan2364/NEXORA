import json
from langchain_core.tools import tool
from src.config import LOYALTY_RULES_FILE

@tool
def calculate_final_price(cart_total: float, loyalty_tier: str, category: str = None):
    """
    Calculates the final price after applying loyalty tier discounts and rules.
    Inputs:
        cart_total: float - total value of items
        loyalty_tier: str - e.g., 'Gold', 'Silver', 'Platinum'
        category: str - e.g., 'Footwear' (optional for category coupons)
    """
    try:
        with open(LOYALTY_RULES_FILE, "r") as f:
            rules = json.load(f)

        discount_breakdown = []
        final_total = cart_total

        # 1. Apply Tier Discount
        tier_rates = rules.get("LOYALTY_TIER_RATES", {})
        tier_discount_percent = tier_rates.get(loyalty_tier, 0.0)
        
        if tier_discount_percent > 0:
            discount_amt = cart_total * tier_discount_percent
            final_total -= discount_amt
            discount_breakdown.append(f"{loyalty_tier} Tier Discount ({int(tier_discount_percent*100)}%): -₹{discount_amt}")

        # 2. Apply Threshold Promotions
        promos = rules.get("THRESHOLD_PROMOTIONS", [])
        for promo in promos:
            if cart_total >= promo["threshold"]:
                if promo["type"] == "flat_discount":
                    final_total -= promo["value"]
                    discount_breakdown.append(f"{promo['description']}: -₹{promo['value']}")

        return {
            "original_total": cart_total,
            "final_total": max(0, final_total),
            "breakdown": discount_breakdown
        }
    except Exception as e:
        return {"error": str(e)}