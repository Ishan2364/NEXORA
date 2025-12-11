import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load the new key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env")
else:
    genai.configure(api_key=api_key)
    print(f"🔑 Testing Key: {api_key[:5]}...")
    
    print("\n---------------- AVAILABLE MODELS ----------------")
    try:
        found = False
        # List all models available to this key
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                found = True
        
        if not found:
            print("⚠️ No content generation models found. Check your API Key permissions.")
    except Exception as e:
        print(f"❌ Error accessing API: {e}")