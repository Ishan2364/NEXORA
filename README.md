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
```bash
git clone [https://github.com/YOUR_USERNAME/nexora-retail-agent.git](https://github.com/YOUR_USERNAME/nexora-retail-agent.git)
cd nexora-retail-agent 
### 2. Backend Setup
```bash
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
