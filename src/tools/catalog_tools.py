import json
import os
from langchain_core.tools import tool
from src.config import DATA_DIR

PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

@tool
def search_catalog(query: str = None, category: str = None):
    """
    Searches the product catalog using keyword matching.
    It ranks results based on how many query terms appear in the product info.
    """
    try:
        with open(PRODUCTS_FILE, "r") as f:
            products = json.load(f)
        
        if not query and not category:
            return products[:5]

        scored_results = []
        
        # Prepare query terms (e.g., "Female Footwear Heels" -> ["female", "footwear", "heels"])
        query_terms = query.lower().split() if query else []

        for p in products:
            # 1. Strict Category Filter (if specifically provided arg, not just in query)
            if category and category.lower() not in p["category"].lower():
                continue
            
            # 2. Keyword Scoring
            # Combine all product text fields for searching
            product_text = f"{p['name']} {p['description']} {p['category']}".lower()
            
            # Count how many keywords exist in this product
            match_count = 0
            for term in query_terms:
                if term in product_text:
                    match_count += 1
            
            # logic: If we have a query, we need at least 1 keyword match.
            # If "heels" is in the name, match_count will be > 0.
            if query and match_count > 0:
                scored_results.append((p, match_count))
            elif not query:
                # If only filtering by category without text query
                scored_results.append((p, 0))
        
        # 3. Sort by Score (Highest matches first)
        # This puts "Premium Leather Heels" (matches 'heels', 'footwear') at the top
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 5 products (stripping the score)
        final_results = [item[0] for item in scored_results[:5]]
        
        if not final_results:
            return "No matching products found."
            
        return final_results

    except Exception as e:
        return f"Error searching catalog: {str(e)}"