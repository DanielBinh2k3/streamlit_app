import streamlit as st

from src.utils.chat_utils import save_current_chat_data
from src.utils.logger import Logger

logger = Logger("chat_callbacks")


def save_chat_parameter(current_chat: str, parameter_name: str) -> None:
    """
    Update the session state when a chat parameter is changed.

    Args:
        current_chat: The name of the current chat
        parameter_name: The parameter that was changed
    """
    if ("history" + current_chat in st.session_state) and (
        "frequency_penalty" + current_chat in st.session_state
    ):
        # Save current chat data
        save_current_chat_data(current_chat)

        # Update value in session state
        st.session_state[parameter_name + current_chat + "value"] = st.session_state[
            parameter_name + current_chat
        ]
        logger.debug(f"Parameter {parameter_name} updated for chat {current_chat}")


def load_session_messages(current_chat: str, session_id: str) -> None:
    """
    Load messages from JSON format into session state format.

    Args:
        current_chat: The name of the current chat
        session_id: The current session ID
    """
    from utils.history_manager import load_conversation_history

    # Load only once at startup
    chat_history = load_conversation_history(session_id)

    # Initialize history if not exists
    if "history" + current_chat not in st.session_state:
        st.session_state["history" + current_chat] = []

    # Convert from history_manager format to current format
    if chat_history:
        for entry in chat_history:
            st.session_state["history" + current_chat].append(
                {
                    "role": "user",
                    "content": entry["input"],
                }
            )
            st.session_state["history" + current_chat].append(
                {
                    "role": "assistant",
                    "content": entry["output"],
                }
            )

    # Mark as loaded
    st.session_state["messages_loaded"] = True
    logger.info(f"Loaded {len(chat_history)} messages for session {session_id}")
