import os
import uuid

import streamlit as st

# Set page configuration
st.set_page_config(page_title="Sunvalue Assistant", page_icon="🦜", layout="wide")

# Initialize session state
if "history_chats" not in st.session_state:
    st.session_state["path"] = "history_chats_file"
    # Create directory if it doesn't exist
    if not os.path.exists(st.session_state["path"]):
        os.makedirs(st.session_state["path"])
    # Initialize with a new chat
    st.session_state["history_chats"] = [f"New Chat_{str(uuid.uuid4())}"]
    st.session_state["current_chat_index"] = 0

# CSS for custom styling
css_code = """
<style>
.main-header {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}
.chat-container {
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}
.user-message {
    background-color: #f0f2f6;
}
.assistant-message {
    background-color: #e6f3ff;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# Main landing page content
st.title("🦜 Sunvalue Assistant")

st.markdown(
    """
Welcome to the Sunvalue Assistant! This tool provides several features to help you:

- **Chat**: Interact with our AI assistant with integrated search capabilities
- **Search**: Test the search function using DuckDuckGo
- **Dashboard**: View analytics and reports (coming soon)
"""
)

# File upload section
st.subheader("Upload Files")
uploaded_files = st.file_uploader(
    "Upload documents for processing",
    accept_multiple_files=True,
    type=["pdf", "txt", "doc", "docx"],
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")

    # Store file references in session state for other pages to access
    if "uploaded_file_data" not in st.session_state:
        st.session_state.uploaded_file_data = []

    file_details = []
    for file in uploaded_files:
        file_details.append({"name": file.name, "type": file.type, "size": file.size})
        # Save file for later use
        with open(os.path.join("uploads", file.name), "wb") as f:
            f.write(file.getbuffer())

    st.session_state.uploaded_file_data = file_details

    st.write(
        "Files ready for processing. Head to the Chat page to interact with your documents."
    )

# Sidebar
with st.sidebar:
    st.title("Navigation")

    # API key input
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        st.session_state.openai_api_key = api_key

    st.markdown("---")
    st.markdown("### Pages")

    # Direct buttons to each page for easier navigation
    if st.button("Chat", use_container_width=True):
        st.switch_page("pages/chat.py")

    if st.button("Search", use_container_width=True):
        st.switch_page("pages/search.py")

    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

    # Chat history section
    st.markdown("---")
    st.markdown("### Recent Chats")

    # Display recent chat history
    for i, chat in enumerate(st.session_state["history_chats"][:5]):
        chat_name = chat.split("_")[0]
        if st.button(f"{chat_name}", key=f"history_{i}", use_container_width=True):
            st.session_state["current_chat_index"] = i
            st.switch_page("pages/chat.py")
