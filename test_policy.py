import os
from dotenv import load_dotenv

# 1. Load API Keys (Ensure .env is in the same folder)
load_dotenv()

# Check if Key exists
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file.")
    exit(1)

# 2. Import the tool directly
try:
    from src.tools.policy_tools import search_return_policy
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you are running this from the root directory.")
    exit(1)

# 3. Define the Test Query
test_query = "Can I return the heels if they hurt?"

print(f"🧪 TESTING: Searching policy for -> '{test_query}'\n")

# 4. Run the Tool
try:
    # Invoke the tool directly with the string
    result = search_return_policy.invoke(test_query)
    
    print("✅ SUCCESS! Result retrieved:\n")
    print("-" * 50)
    print(result)
    print("-" * 50)

    # 5. Logical Verification
    if "Footwear" in result or "30 Days" in result:
        print("\n🎯 VERIFIED: The tool found the correct 'Footwear' policy.")
    else:
        print("\n⚠️ WARNING: The tool ran, but didn't return specific 'Footwear' keywords. Check PDF content.")

except Exception as e:
    print(f"\n❌ FAILED: The tool crashed.\nError: {e}")