import hashlib
from typing import Any, Dict, List, Tuple

import streamlit as st

from src.utils.helper import set_context_all
from src.utils.history_manager import get_history_input
from src.utils.logger import Logger

logger = Logger("chat_utils")


def prepare_model_input(
    current_chat: str, context_level: int = None
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """
    Prepare the chat history and parameters for the model.

    Args:
        current_chat: The name of the current chat
        context_level: The context level to use (default: None, will use the value from session state)

    Returns:
        tuple: (history, parameters)
            - history: List of messages to send to the model
            - parameters: Dictionary of model parameters
    """
    if context_level is None:
        context_level = st.session_state.get("context_level" + current_chat, 3)

    # Format history for model input
    history = get_history_input(
        st.session_state["history" + current_chat], context_level
    )

    if "pre_user_input_content" in st.session_state:
        history.append(
            {
                "role": "user",
                "content": st.session_state["pre_user_input_content"],
            }
        )

    # Add context if available
    context_select = st.session_state.get("context_select" + current_chat, "Mặc định")
    context_input = st.session_state.get("context_input" + current_chat, "")

    for ctx in [context_input, set_context_all.get(context_select, "")]:
        if ctx != "":
            history = [{"role": "system", "content": ctx}] + history

    # Model parameters
    parameters = {
        "temperature": st.session_state.get("temperature" + current_chat, 0.7),
        "top_p": st.session_state.get("top_p" + current_chat, 0.7),
        "presence_penalty": st.session_state.get(
            "presence_penalty" + current_chat, 0.7
        ),
        "frequency_penalty": st.session_state.get(
            "frequency_penalty" + current_chat, 0.7
        ),
    }

    return history, parameters


def save_chat_parameters(current_chat: str, arg: str) -> None:
    """
    Update the session state when a parameter is changed.

    Args:
        current_chat: The name of the current chat
        arg: The parameter name that was changed
    """
    if ("history" + current_chat in st.session_state) and (
        "frequency_penalty" + current_chat in st.session_state
    ):
        # Save the parameter to session state
        st.session_state[arg + current_chat + "value"] = st.session_state[
            arg + current_chat
        ]


def save_current_chat_data(current_chat: str, new_chat_name: str = None) -> None:
    """
    Save the current chat data to file using the legacy format.

    Args:
        current_chat: The name of the current chat session
        new_chat_name: Optional new name for the chat (default: None)
    """
    from utils.history_manager import save_legacy_chat

    target_chat = new_chat_name or current_chat
    logger.debug(f"Saving chat data for {target_chat}")

    # Collect parameters
    parameters = {
        "temperature": st.session_state.get("temperature" + current_chat, 0.7),
        "top_p": st.session_state.get("top_p" + current_chat, 0.7),
        "presence_penalty": st.session_state.get(
            "presence_penalty" + current_chat, 0.7
        ),
        "frequency_penalty": st.session_state.get(
            "frequency_penalty" + current_chat, 0.7
        ),
    }

    # Collect context
    contexts = {
        "context_select": st.session_state.get(
            "context_select" + current_chat, "Mặc định"
        ),
        "context_input": st.session_state.get("context_input" + current_chat, ""),
        "context_level": st.session_state.get("context_level" + current_chat, 3),
    }

    # Save to legacy format
    save_legacy_chat(
        target_chat, st.session_state["history" + current_chat], parameters, contexts
    )


def generate_conversation_id(prompt: str) -> str:
    """
    Generate a unique conversation ID from the prompt.

    Args:
        prompt: The user's input prompt

    Returns:
        str: A unique conversation ID
    """
    # Use the first part of the prompt to create a readable ID
    return f"conv-{hashlib.md5(prompt[:20].encode()).hexdigest()[:10]}"
