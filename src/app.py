import sys
import os

# --- FIX: Force Python to see the 'src' folder ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# -------------------------------------------------

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_retail_graph

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ABFRL Retail Agent",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 🎨 PREMIUM UI OVERHAUL (CSS) ---
st.markdown("""
<style>
    /* 1. IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* 2. FORCE LIGHT THEME & TYPOGRAPHY */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
        color: #000000;
    }
    
    /* 3. APP CONTAINER */
    .stApp {
        background-color: #ffffff;
    }

    /* 4. SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.2rem;
        font-weight: 700;
        color: #111;
        margin-bottom: 20px;
    }

    /* 5. CHAT BUBBLES - CLEAN & CONTRAST */
    /* User Message (Black Bubble, White Text) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #ffffff; /* Transparent wrapper */
    }
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) div[data-testid="stMarkdownContainer"] {
        background-color: #000000;
        color: #ffffff !important;
        padding: 12px 18px;
        border-radius: 18px 18px 0 18px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Agent Message (Light Grey Bubble, Black Text) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) div[data-testid="stMarkdownContainer"] {
        background-color: #f1f3f5;
        color: #111111 !important;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0;
    }

    /* 6. FIX THE CHAT INPUT (The Grey Problem) */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .stChatInputContainer textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 12px;
    }
    .stChatInputContainer textarea:focus {
        border-color: #000000 !important;
        box-shadow: 0 0 0 2px rgba(0,0,0,0.1) !important;
    }

    /* 7. LOGIN PAGE - CENTERED CARD */
    .login-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin-top: 10vh;
    }
    .login-header {
        font-size: 3rem;
        font-weight: 700;
        color: #000;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    .login-sub {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 3rem;
    }
    
    /* Button Styling */
    .stButton button {
        background-color: #000 !important;
        color: #fff !important;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: transform 0.1s ease;
    }
    .stButton button:hover {
        background-color: #222 !important;
        transform: translateY(-1px);
    }

</style>
""", unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if "graph" not in st.session_state:
    st.session_state.graph = create_retail_graph()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_platform" not in st.session_state:
    st.session_state.current_platform = "Website"

# --- HELPER: Process Chat ---
def process_message(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    inputs = {"messages": [HumanMessage(content=user_input)]}
    config = {"configurable": {"thread_id": st.session_state.user_id}}
    
    # Spinner styling
    with st.spinner(f"Agent is thinking..."):
        try:
            output_msg = None
            for event in st.session_state.graph.stream(inputs, config=config):
                for key, value in event.items():
                    if key not in ["supervisor", "tools"] and "messages" in value:
                        last_msg = value["messages"][-1]
                        if isinstance(last_msg, AIMessage) and last_msg.content:
                            output_msg = last_msg.content
            
            if output_msg:
                st.session_state.messages.append({"role": "assistant", "content": output_msg})
            else:
                 st.session_state.messages.append({"role": "assistant", "content": "I'm working on that..."})

        except Exception as e:
            st.error(f"System Error: {e}")

# --- LOGIN PAGE ---
def login_page():
    # Use empty columns to center the content perfectly
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<div class='login-header'>ABFRL.</div>", unsafe_allow_html=True)
        st.markdown("<div class='login-sub'>Unified Retail Intelligence</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("login_form"):
            st.text_input("Customer ID", key="username", placeholder="e.g., CUST001")
            st.text_input("Password", type="password", placeholder="••••••")
            
            if st.form_submit_button("Sign In", use_container_width=True):
                user = st.session_state.username.upper()
                valid_users = ["CUST001", "CUST002", "CUST003", "CUST004"]
                
                if user in valid_users:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user
                    process_message(f"SYSTEM: User {user} logged in via {st.session_state.current_platform}")
                    st.rerun()
                else:
                    st.error("Invalid Customer ID. Try CUST001")

# --- MAIN APP ---
def main_app():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### Welcome, **{st.session_state.user_id}**")
        st.caption("Gold Tier Member")
        st.markdown("---")
        
        st.markdown("### 📱 Platform")
        platform_options = ["Website", "Mobile App", "In-Store Kiosk"]
        
        new_platform = st.radio(
            "Select Interface:",
            options=platform_options,
            index=platform_options.index(st.session_state.current_platform),
            label_visibility="collapsed"
        )
        
        if new_platform != st.session_state.current_platform:
            st.session_state.current_platform = new_platform
            process_message(f"SYSTEM_NOTE: User switched to {new_platform}. Briefly summarize context.")
            st.rerun()

        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    # Chat Header
    st.markdown(f"### {st.session_state.current_platform} Support")
    st.markdown("---")

    # Chat History
    for msg in st.session_state.messages:
        if "SYSTEM" in msg["content"]: continue
        
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Area
    if prompt := st.chat_input("How can I help you today?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        process_message(prompt)
        st.rerun()

# --- RUNNER ---
if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()