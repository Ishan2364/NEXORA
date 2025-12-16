import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Force reload .env
load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")

print(f"🔹 Python sees this key: {key[:5]}...{key[-4:] if key else 'None'}")

if not key:
    print("❌ ERROR: No key found! Check your .env file.")
    exit()

try:
    # 2. Try a real call
    llm = ChatGroq(model="openai/gpt-oss-120b", api_key=key)
    res = llm.invoke("Hello")
    print("✅ SUCCESS! The key is working.")
    print(f"Response: {res.content}")
except Exception as e:
    print(f"❌ AUTH FAILED: {e}")