import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing. Please add it to your .env file.")

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
LOYALTY_RULES_FILE = os.path.join(DATA_DIR, "loyalty_rules.json")
POLICY_DOC_PATH = os.path.join(DATA_DIR, "docs", "policy.abfrl.pdf")