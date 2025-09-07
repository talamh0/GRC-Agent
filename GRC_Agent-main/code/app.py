import streamlit as st
import os
from PIL import Image
from agent_prep import get_agent_response, initialize_agent

# ========== Initialize Session State ==========
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default language is English
if 'agent' not in st.session_state:
    st.session_state.agent, _ = initialize_agent() # Initialize the agent once
if 'config' not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "streamlit_session"}}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
# ========== Text Translations ==========
translations = {
    'en': {
        'page_title': "GRC Agent | Saudi Cybersecurity Assistant",
        'banner_title': "🤖 GRC Agent – Saudi Cybersecurity Chatbot",
        'welcome_text': "Welcome to the Governance, Risk & Compliance (GRC) assistant powered by Saudi NCA guidelines.",
        'input_placeholder': "📝 Ask your question below:",
        'submit_button': "🔍 Submit",
        'response_title': "### 💡 GRC Agent Response:",
        'empty_input_warning': "⚠️ Please enter a valid question.",
        'language_button': "🌐 العربية"
    },
    'ar': {
        'page_title': "مساعد الأمن السيبراني السعودي | GRC Agent",
        'banner_title': "🤖 مساعد الأمن السيبراني السعودي",
        'welcome_text': " المدعوم بإرشادات الهيئة الوطنية للأمن السيبراني السعودي(GRC)مرحبًا بك في مساعد الحوكمة والمخاطر والامتثال",   
        'input_placeholder': "📝 اكتب سؤالك هنا:",
        'submit_button': "🔍 إرسال",
        'response_title': "### 💡 رد المساعد:",
        'empty_input_warning': "⚠️ الرجاء إدخال سؤال صحيح.",
        'language_button': "🌐 English"
    }
}

# Function to get text based on current language
def get_text(key):
    return translations[st.session_state.language][key]

# ========== UI ==========

st.set_page_config(page_title=get_text('page_title'), layout="wide")

# Load external CSS using a more reliable method
def local_css(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Get the absolute path to the CSS file
css_path = os.path.join(os.path.dirname(__file__), 'static', 'style.css')
local_css(css_path)

# Set a darker blue background color (dark mode) with enhanced aesthetics
st.markdown("""
    <style>
    .stApp {
        background-color: #0a1128; /* Even darker blue for dark mode */
        background-image: linear-gradient(to bottom right, #0a1128, #1a2a57); /* Gradient background */
    }
    
    /* Add a custom background for the main content area */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin-top: -3rem; /* Further reduce space between elements */
    }
    
    /* Increase font size for all text */
    p, div, span, h1, h2, h3, h4, h5, h6 {
        font-size: 1.25rem !important;
    }
    
    /* Make headings even larger with better styling */
    h1 {
        font-size: 2.5rem !important;
        color: #4a90e2 !important;
        margin-top: -2rem !important; /* Further reduce space after image */
        margin-bottom: 0.5rem !important; /* Reduce space below heading */
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        font-size: 2rem !important;
        color: #3a7bc8 !important;
    }
    
    h3 {
        font-size: 1.75rem !important;
        color: #2c5d99 !important;
    }
    
    /* Style for chat input */
    .stChatInput > div > div > input {
        background-color: rgba(10, 17, 40, 0.8) !important; /* Dark background with some transparency */
        color: white !important; /* Text color for better contrast */
        border: 1px solid #4a90e2 !important;
        border-radius: 10px !important;
        padding: 0.5em !important;
        font-size: 1em !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create a header row with icon on left and language button on right
col1, col2, col3 = st.columns([1, 5, 1])

# Display the icon on the left
with col1:
    nca_logo_path = os.path.join(os.path.dirname(__file__), 'static', 'NCA logo.jpg')
    st.image(nca_logo_path, width=90, caption="", clamp=True, output_format="auto")

# Language toggle button on the right
with col3:
    if st.button(get_text('language_button')):
        # Toggle language
        st.session_state.language = 'ar' if st.session_state.language == 'en' else 'en'
        st.rerun()

# Title below the image
st.title(get_text('banner_title'))

# Welcome text below the title
st.markdown(get_text('welcome_text'))

# 📦 Main content with chat interface
content_class = "content" + (" arabic" if st.session_state.language == 'ar' else "")
st.markdown(f'<div class="{content_class}">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(get_text('input_placeholder')):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response from the agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Show a temporary message while waiting for the response
        message_placeholder.markdown("-thinking...▌")
        
        try:
            full_response = get_agent_response(prompt, st.session_state.agent, st.session_state.config)
            
            # Simulate typing effect
            import time
            displayed_response = ""
            for chunk in full_response.split():
                displayed_response += chunk + " "
                message_placeholder.markdown(displayed_response + "▌")
                time.sleep(0.05)
            
            # Display full response
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"An error occurred: {e}"
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown('</div>', unsafe_allow_html=True)
