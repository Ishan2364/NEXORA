import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY not found in .env")
else:
    print(f"🔑 Testing Key: {api_key[:5]}...")

    try:
        client = Groq(api_key=api_key)

        print("\n---------------- AVAILABLE MODELS ----------------")

        models = client.models.list()

        if models.data:
            for m in models.data:
                print(f"✅ {m.id}")
        else:
            print("⚠️ No models available for this API key.")

    except Exception as e:
        print(f"❌ Error accessing Groq API: {e}")
