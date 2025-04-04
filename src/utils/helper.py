from typing import Any, Dict, List, Optional

# Constants
ICON = "🦜"

# Initial model parameters
initial_content_all = {
    "paras": ["temperature", "top_p", "presence_penalty", "frequency_penalty"],
}

# Context presets
set_context_all = {
    "Mặc định": "",
}


def show_each_message(
    content: str,
    role: str,
    key: Optional[str] = None,
    containers: Optional[List[Any]] = None,
) -> None:
    """Display a single message."""
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤" if role == "user" else "🤖"

    message_html = f"""
    <div class="chat-container {css_class}">
        <p><strong>{icon}</strong></p>
        <div>{content}</div>
    </div>
    """

    if containers:
        containers[0](f"<strong>{icon}</strong>", unsafe_allow_html=True)
        containers[1](content, unsafe_allow_html=True)
    else:
        # Default to st.markdown if no containers provided
        import streamlit as st

        st.markdown(message_html, unsafe_allow_html=True)


def show_messages(chat_id: str, messages: List[Dict[str, str]]) -> None:
    """Display all messages in the chat history."""
    import streamlit as st

    if not messages:
        return

    for i, msg in enumerate(messages):
        if msg["role"] != "system":
            with st.container():
                show_each_message(msg["content"], msg["role"], f"{chat_id}_{i}")
