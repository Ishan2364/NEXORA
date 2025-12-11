# 👑 Nexora Retail Agent

> **Where Luxury Meets Intelligence.**

Nexora is an advanced **Agentic AI System** designed to revolutionize the luxury retail experience. Unlike traditional chatbots, Nexora uses a **Multi-Agent Architecture** (powered by LangGraph) to autonomously manage the entire customer journey—from personalized recommendations and inventory checks to secure payments and invoice generation.

The frontend features a **"Royal Gold" Glassmorphism UI**, providing a premium, immersive experience across Web, Mobile, and Kiosk interfaces.

![Nexora Banner](https://via.placeholder.com/1200x600/0a0a0a/d4af37?text=Nexora+Retail+Intelligence)
*(Replace this link with a real screenshot of your dashboard later)*

---

## ✨ Key Features

### 🧠 **Autonomous Multi-Agent Brain**
Nexora isn't just one AI. It is a team of specialized agents coordinated by a **Supervisor**:
- **🛍️ Recommendation Agent:** Suggests products based on user profile and history.
- **📦 Inventory Agent:** Checks real-time stock levels across stores.
- **💎 Loyalty Agent:** Calculates dynamic pricing based on "Gold/Platinum" tiers.
- **💳 Secure Payment Agent:** Handles UPI (QR Code) and Credit Card transactions securely.
- **🚚 Fulfillment Agent:** Orchestrates delivery, logistics, and invoice generation.

### 🎨 **"Royal" Agentic UI**
The interface is aware of the AI's intent. It renders specialized components dynamically based on hidden agent signals:
- **Dynamic QR Codes:** Renders real, scannable UPI QR codes in-chat.
- **Secure Forms:** Pops up secure input fields for sensitive data like credit cards.
- **Digital Receipts:** Auto-generates and stores beautiful digital invoices.
- **Live Dashboard:** Tracks purchase history and profile status in real-time.

---

## 🛠️ Tech Stack

### **Backend (The Brain)**
- **Python 3.12+**
- **FastAPI:** High-performance API layer.
- **LangGraph:** For stateful, cyclic multi-agent orchestration.
- **LangChain:** Tooling and LLM interfaces.
- **Groq API (Llama 3.1 8B):** Ultra-low latency inference for real-time chat.

### **Frontend (The Face)**
- **React.js (Vite):** Blazing fast UI framework.
- **CSS Modules:** Custom "Royal Rose Gold" design system.
- **Lucide React:** Premium iconography.
- **Axios:** For seamless API communication.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js & npm
- A [Groq API Key](https://console.groq.com)

### 1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/nexora-retail-agent.git](https://github.com/YOUR_USERNAME/nexora-retail-agent.git)
cd nexora-retail-agent


### 2. Backend Setup
Bash
# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Environment Variables
# Create a .env file in the root and add your key:
echo "GROQ_API_KEY=gsk_your_key_here" > .env

###3. Frontend Setup
Bash

# Open a new terminal in the project root
npm install

🏃‍♂️ Running the Application
You need to run the Backend and Frontend simultaneously in two separate terminals.

Terminal 1: Backend

Bash

uvicorn src.api:app --reload
Server will start at: http://127.0.0.1:8000

Terminal 2: Frontend

Bash

npm run dev
App will start at: http://localhost:5173

🧪 Demo Flow to Try
Login: Use ID CUST001 (Password: any).

Browse: Ask "Show me some red dresses."

Buy: Say "I want to buy the first one."

Loyalty: The agent will calculate your discount based on your tier.

Pay: Choose UPI. Scan the QR code (or type "Done").

Invoice: The agent will generate a digital receipt.

Dashboard: Go to the Invoices tab to see your new permanent record.

📂 Project Structure
nexora-retail-agent/
├── src/
│   ├── agents/          # Worker definitions & Prompts
│   ├── graph/           # LangGraph Workflow & State
│   ├── tools/           # Python Tools (CRM, Inventory, Invoice)
│   ├── api.py           # FastAPI Entry Point
│   ├── App.jsx          # Main React UI
│   └── index.css        # Royal Theme Styles
├── data/                # JSON Mock Databases (Products, Users)
├── requirements.txt     # Python Dependencies
└── README.md            # Documentation
🛡️ License
This project is licensed under the MIT License - see the LICENSE file for details.

<p align="center"> Built with ❤️ by <b>Rocky</b> | Powered by <b>Groq & LangGraph</b> </p>
