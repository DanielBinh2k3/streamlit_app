import streamlit as st
from streamlit.components import v1

from src.utils.logger import Logger

logger = Logger("streamlit_utils")


def clear_button_callback(current_chat: str) -> None:
    """
    Clear the current chat history both in legacy and new format.

    Args:
        current_chat: The name of the current chat session
    """
    # Clear legacy format
    st.session_state["history" + current_chat] = []

    # Import here to avoid circular imports
    from src.utils.chat_utils import save_current_chat_data
    from src.utils.history_manager import clear_session_history

    save_current_chat_data(current_chat)

    # Also clear in the new history format if session_id exists
    if "session_id" in st.session_state:
        clear_session_history(st.session_state["session_id"])


def initialize_page() -> None:
    """Initialize the Streamlit page with common configuration."""
    st.set_page_config(
        page_title="Chat | Sunvalue Assistant", page_icon="🦜", layout="wide"
    )


def apply_js_code() -> None:
    """Apply custom JavaScript to the Streamlit app."""
    # Import here to avoid circular imports
    from src.utils.js_utils import js_code

    # Add custom JavaScript
    v1.html(js_code, height=0)
