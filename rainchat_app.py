import streamlit as st
import openai
import time
import random
import html
import os
from dotenv import load_dotenv
import google.generativeai as genai  # Import Google's Generative AI library

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="RainChat AI Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced Rain theme
def add_rain_theme():
    rain_css = """
    <style>
    /* Main theme colors and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');
    
    .stApp {
        background-color: #0a192f;
        color: #e6f1ff;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Rain Animation Background */
    .rain-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        z-index: -1;
    }
    
    .rain-drop {
        position: absolute;
        pointer-events: none;
        color: rgba(0, 195, 255, 0.4);
        font-family: monospace;
        font-size: 14px;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 195, 255, 0.7);
        animation: rainFall linear infinite;
    }
    
    @keyframes rainFall {
        0% { transform: translateY(-100px); opacity: 0; }
        10% { opacity: 1; }
        95% { opacity: 1; }
        100% { transform: translateY(100vh); opacity: 0; }
    }
    
    /* Custom Chat UI */
    .chat-container {
        margin: 0 auto;
        max-width: 800px;
        background-color: rgba(13, 33, 63, 0.7);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #234976;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
    }
    
    .chat-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid #234976;
        padding-bottom: 15px;
    }
    
    .chat-logo {
        width: 40px;
        height: 40px;
        margin-right: 15px;
        background-color: #00c3ff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: #0a192f;
    }
    
    .user-message {
        background-color: rgba(18, 45, 82, 0.6);
        color: #ffffff;
        border-radius: 18px 18px 5px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        border: 1px solid #234976;
    }
    
    .bot-message {
        background-color: rgba(0, 122, 158, 0.15);
        color: #e6f1ff;
        border-radius: 18px 18px 18px 5px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-right: auto;
        border: 1px solid rgba(0, 195, 255, 0.3);
    }
    
    .message-timestamp {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 5px;
        text-align: right;
    }
    
    /* Input area styling */
    .chat-input-area {
        background-color: rgba(13, 33, 63, 0.7);
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
        border: 1px solid #234976;
    }
    
    .stTextInput input {
        background-color: rgba(30, 55, 95, 0.5) !important;
        border: 1px solid #3a6ea5 !important;
        border-radius: 25px !important;
        color: white !important;
        padding: 10px 20px !important;
    }
    
    .stButton button {
        background-color: #00c3ff !important;
        color: #0a192f !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        padding: 5px 20px !important;
        border: none !important;
    }
    
    .st-bc {
        background-color: rgba(13, 33, 63, 0.7) !important;
    }
    
    .sidebar-content {
        background-color: rgba(13, 33, 63, 0.7);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #234976;
    }
    
    /* Model selection tabs */
    .model-selector {
        display: flex;
        margin-bottom: 15px;
    }
    
    .model-tab {
        flex: 1;
        text-align: center;
        padding: 10px;
        cursor: pointer;
        border: 1px solid #234976;
        background-color: rgba(13, 33, 63, 0.5);
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.3s ease;
    }
    
    .model-tab.active {
        background-color: rgba(0, 195, 255, 0.2);
        color: #00c3ff;
        border-color: #00c3ff;
        font-weight: bold;
    }
    
    .model-tab:first-child {
        border-radius: 8px 0 0 8px;
    }
    
    .model-tab:last-child {
        border-radius: 0 8px 8px 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 33, 63, 0.3);
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00c3ff;
        border-radius: 10px;
    }
    </style>
    """
    
    rain_js = """
    <script>
    function createRaindrops() {
        const container = document.createElement('div');
        container.className = 'rain-container';
        document.body.appendChild(container);
        
        const characters = '10アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        const dropCount = 100;
        
        for (let i = 0; i < dropCount; i++) {
            setTimeout(() => {
                const drop = document.createElement('div');
                drop.className = 'rain-drop';
                
                // Randomize drop properties
                const size = Math.random() * 14 + 10;
                const speed = Math.random() * 10 + 5;
                const delay = Math.random() * 5;
                const leftPos = Math.random() * 100;
                const char = characters.charAt(Math.floor(Math.random() * characters.length));
                
                drop.style.left = leftPos + 'vw';
                drop.style.fontSize = size + 'px';
                drop.style.animationDuration = speed + 's';
                drop.style.animationDelay = delay + 's';
                drop.style.opacity = Math.random() * 0.5 + 0.2;
                drop.innerHTML = char;
                
                container.appendChild(drop);
                
                // Create a stream effect by adding characters in the same column
                const streamLength = Math.floor(Math.random() * 10) + 3;
                for (let j = 1; j < streamLength; j++) {
                    setTimeout(() => {
                        const streamDrop = document.createElement('div');
                        streamDrop.className = 'rain-drop';
                        streamDrop.style.left = leftPos + 'vw';
                        streamDrop.style.fontSize = size + 'px';
                        streamDrop.style.animationDuration = speed + 's';
                        streamDrop.style.animationDelay = (delay + j * 0.2) + 's';
                        streamDrop.style.opacity = Math.random() * 0.5 + 0.2;
                        streamDrop.innerHTML = characters.charAt(Math.floor(Math.random() * characters.length));
                        container.appendChild(streamDrop);
                    }, j * 200);
                }
                
                // Remove after animation completes
                setTimeout(() => {
                    drop.remove();
                }, (speed + delay) * 1000);
                
            }, i * 100);
        }
        
        // Continuously add new drops
        setInterval(createNewDrop, 1000);
    }
    
    function createNewDrop() {
        const container = document.querySelector('.rain-container');
        if (!container) return;
        
        const characters = '10アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        const drop = document.createElement('div');
        drop.className = 'rain-drop';
        
        const size = Math.random() * 14 + 10;
        const speed = Math.random() * 10 + 5;
        const leftPos = Math.random() * 100;
        
        drop.style.left = leftPos + 'vw';
        drop.style.fontSize = size + 'px';
        drop.style.animationDuration = speed + 's';
        drop.style.opacity = Math.random() * 0.5 + 0.2;
        drop.innerHTML = characters.charAt(Math.floor(Math.random() * characters.length));
        
        container.appendChild(drop);
        
        // Remove after animation completes
        setTimeout(() => {
            drop.remove();
        }, speed * 1000);
    }
    
    document.addEventListener('DOMContentLoaded', createRaindrops);
    </script>
    
    <div class="chat-header">
        <div class="chat-logo">RC</div>
        <h2>RainChat AI Assistant</h2>
    </div>
    """
    
    st.markdown(rain_css, unsafe_allow_html=True)
    st.markdown(rain_js, unsafe_allow_html=True)

add_rain_theme()

# Get API keys from environment variables or .env file
openai_api_key = os.getenv("OPENAI_API_KEY", "")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "openai"  # Default model

if 'form_submit' not in st.session_state:
    st.session_state.form_submit = False

# Check if API keys are set
def is_openai_key_set():
    return st.session_state.get('temp_openai_key', openai_api_key) != ""

def is_gemini_key_set():
    return st.session_state.get('temp_gemini_key', gemini_api_key) != ""

# Function to get current time
def get_time():
    return time.strftime("%I:%M %p")

# Function to generate response from OpenAI
def get_openai_response(prompt):
    try:
        api_key = st.session_state.get('temp_openai_key', openai_api_key)
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Keep your responses under 100 words."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate response from Gemini
def get_gemini_response(prompt):
    try:
        api_key = st.session_state.get('temp_gemini_key', gemini_api_key)
        
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Create a GenerativeModel object
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate a response
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 150,
            }
        )
        
        # Extract the text from the response
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# General get response function that routes to the appropriate API
def get_chatbot_response(prompt):
    if st.session_state.selected_model == "openai":
        return get_openai_response(prompt)
    else:  # gemini
        return get_gemini_response(prompt)

# Sidebar for API key setup
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.subheader("Setup")
    
    # Model selection
    st.write("Select AI Model:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("OpenAI", key="select_openai", 
                    use_container_width=True,
                    type="primary" if st.session_state.selected_model == "openai" else "secondary"):
            st.session_state.selected_model = "openai"
            st.rerun()
    
    with col2:
        if st.button("Gemini", key="select_gemini", 
                    use_container_width=True,
                    type="primary" if st.session_state.selected_model == "gemini" else "secondary"):
            st.session_state.selected_model = "gemini"
            st.rerun()
    
    st.divider()
    
    # API Key inputs based on selected model
    if st.session_state.selected_model == "openai":
        st.subheader("OpenAI API Setup")
        if not is_openai_key_set():
            st.warning("⚠️ OpenAI API key not found!")
            st.info("Option 1: Create a .env file with OPENAI_API_KEY=your_api_key")
            st.info("Option 2: Enter your API key below (temporary, not saved):")
            temp_api_key = st.text_input("OpenAI API Key:", type="password", key="openai_key_input")
            if temp_api_key:
                st.session_state.temp_openai_key = temp_api_key
                st.success("✅ OpenAI API Key set for this session")
        else:
            st.success("✅ OpenAI API Key configured")
    else:  # gemini
        st.subheader("Gemini API Setup")
        if not is_gemini_key_set():
            st.warning("⚠️ Gemini API key not found!")
            st.info("Option 1: Create a .env file with GEMINI_API_KEY=your_api_key")
            st.info("Option 2: Enter your API key below (temporary, not saved):")
            temp_api_key = st.text_input("Gemini API Key:", type="password", key="gemini_key_input")
            if temp_api_key:
                st.session_state.temp_gemini_key = temp_api_key
                st.success("✅ Gemini API Key set for this session")
        else:
            st.success("✅ Gemini API Key configured")
    
    st.divider()
    st.subheader("About")
    st.markdown(f"RainChat uses {'OpenAI GPT-3.5' if st.session_state.selected_model == 'openai' else 'Google Gemini'} to provide helpful responses.")
    st.markdown("All responses are limited to around 100 words or less.")
    st.markdown("</div>", unsafe_allow_html=True)

# Display model badge on the main interface
model_badge = "OpenAI GPT-3.5" if st.session_state.selected_model == "openai" else "Google Gemini"
st.caption(f"Using: {model_badge}")

# Main chat interface
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            {html.escape(message['content'])}
            <div class="message-timestamp">{message['time']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            {html.escape(message['content'])}
            <div class="message-timestamp">{message['time']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input area
st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)

# Check if the currently selected API key is set
api_ready = (is_openai_key_set() if st.session_state.selected_model == "openai" else is_gemini_key_set())

# Using a form for message submission
with st.form(key="chat_form"):
    user_input = st.text_input("", placeholder="Type your message here...")
    col1, col2 = st.columns([5, 1])
    
    with col2:
        submit_button = st.form_submit_button("Send", disabled=not api_ready)

# Display warning if API key is not set
if not api_ready:
    st.warning(f"⚠️ Please enter your {'OpenAI' if st.session_state.selected_model == 'openai' else 'Gemini'} API key in the sidebar to start chatting.")

# Process the form submission
if submit_button and user_input and api_ready:
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user", 
        "content": user_input,
        "time": get_time()
    })
    
    # Get response from selected AI model
    with st.spinner("Thinking..."):
        response = get_chatbot_response(user_input)
    
    # Add response to chat history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response,
        "time": get_time()
    })
    
    # Force a rerun to update the UI
    st.rerun()

# Outside the form - Clear chat button
if st.session_state.chat_history:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Instructions for deployment
if not st.session_state.chat_history:
    st.markdown(f"""
    <div style="margin-top: 30px; text-align: center; color: rgba(255,255,255,0.6);">
        <h4>👋 Welcome to RainChat!</h4>
        <p>Type a message above to start chatting with the {model_badge} assistant.</p>
        <p>You can switch between OpenAI and Gemini in the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)

# Add footer
st.markdown("""
<div style="position: fixed; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 12px; color: rgba(255,255,255,0.5);">
    © 2025 RainChat AI Assistant | Built with Streamlit
</div>
""", unsafe_allow_html=True)
