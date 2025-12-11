import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load env variables
load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 Using Key: {key[:5]}... (checking connectivity)")

# Try to list models using the LangChain wrapper
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001", google_api_key=key)
    # We will try a simple invoke to see if the specific version works
    print("Attempting to connect with 'gemini-1.5-flash-001'...")
    response = llm.invoke("Hello, are you there?")
    print(f"✅ SUCCESS! Model used: gemini-1.5-flash-001")
    print(f"🤖 Response: {response.content}")
except Exception as e:
    print(f"❌ Failed on flash-001. Error:\n{e}")

print("\n--- Trying standard 'gemini-pro' ---")
try:
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=key)
    response = llm.invoke("Hello?")
    print(f"✅ SUCCESS! Model used: gemini-pro")
except Exception as e:
    print(f"❌ Failed on gemini-pro.")