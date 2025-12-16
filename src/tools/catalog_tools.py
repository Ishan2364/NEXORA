import json
import os
from langchain_core.tools import tool
from src.config import DATA_DIR

# Load the new rich product data
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)

def format_product_card(p):
    """
    Creates a Markdown formatted card for the Agent to read 
    and the Frontend to render.
    """
    # 1. Image Logic: Markdown Image Syntax
    # The frontend MarkdownRenderer will turn this into a real <img> tag
    image_md = f"![{p['name']}]({p.get('image_url', '')})"
    
    # 2. Size & Color Logic
    sizes = ", ".join(p.get("sizes", []))
    colors = ", ".join(p.get("colors", []))
    
    # 3. Social Proof (Rating)
    rating = p.get("social_proof", {}).get("rating", "New")
    reviews = p.get("social_proof", {}).get("reviews_count", 0)

    # 4. Construct the Card
    return f"""
---
### **{p['name']}**
{image_md}

**Price:** ₹{p['price']} (MRP: ₹{p.get('mrp', p['price'])})
**Brand:** {p.get('brand', 'Nexora')}
**Rating:** ⭐ {rating} ({reviews} reviews)

**Details:**
- **Sizes:** {sizes}
- **Colors:** {colors}
- **Description:** {p.get('description', '')}

**SKU:** `{p['sku']}`
---
"""

@tool
def search_catalog(query: str):
    """
    Searches the product catalog by text (name, category, tags, color).
    Returns formatted product cards with images.
    """
    products = load_products()
    query = query.lower().strip()
    
    results = []
    
    # Simple Keyword Search Engine
    for p in products:
        # Create a giant searchable string for this product
        searchable_text = f"{p['name']} {p['category']} {p.get('sub_category','')} {' '.join(p.get('tags', []))} {' '.join(p.get('colors', []))}".lower()
        
        # Check if all parts of the user query are in the product (fuzzy match)
        # e.g., "Red Dress" -> checks if 'red' AND 'dress' exist in data
        query_terms = query.split()
        if all(term in searchable_text for term in query_terms):
            results.append(p)
    
    # If no results, try partial match (any term)
    if not results:
        for p in products:
            searchable_text = f"{p['name']} {p['category']}".lower()
            if any(term in searchable_text for term in query_terms):
                results.append(p)

    # Limit results to top 5 to avoid overwhelming the LLM
    results = results[:5]
    
    if not results:
        return "No products found matching your criteria. Suggest looking for 'Dresses', 'Heels', or 'Jackets'."

    # Format output
    return "\n".join([format_product_card(p) for p in results])