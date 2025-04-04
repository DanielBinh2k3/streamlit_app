import json
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Tuple

import streamlit as st

from src.utils.logger import Logger

logger = Logger("history_manager")

# Constants for history paths
LEGACY_HISTORY_PATH = "history_chats_file"
JSON_HISTORY_PATH = os.path.join(LEGACY_HISTORY_PATH, "sessions")


def generate_session_id() -> str:
    """Generate a unique session ID for a new conversation."""
    return str(uuid.uuid4())


def get_history_file_path(session_id: str) -> str:
    """Get the file path for a session's history file."""
    # Create the history directory if it doesn't exist
    os.makedirs(JSON_HISTORY_PATH, exist_ok=True)
    return os.path.join(JSON_HISTORY_PATH, f"{session_id}.json")


def get_legacy_file_path(chat_name: str) -> str:
    """Get the file path for a legacy chat file."""
    os.makedirs(LEGACY_HISTORY_PATH, exist_ok=True)
    return os.path.join(LEGACY_HISTORY_PATH, f"{chat_name}.json")


def filename_correction(filename: str) -> str:
    """Sanitize filename to be valid."""
    # Remove invalid characters for filenames
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def extract_chars(text: str, limit: int = 18) -> str:
    """Extract the first few characters from text for naming."""
    if not text:
        return "New Chat"

    # Remove special characters and whitespace
    text = re.sub(r"[^\w\s]", "", text)
    text = text.strip()

    if len(text) <= limit:
        return text
    else:
        return text[:limit] + "..."


# Initialize session state for chat history
def initialize_chat_history():
    """Initialize the session state variables for chat history."""
    if "history_chats" not in st.session_state:
        logger.info("Initializing new history_chats")
        st.session_state["path"] = LEGACY_HISTORY_PATH
        # Create a default chat entry
        st.session_state["history_chats"] = ["New Chat_" + str(uuid.uuid4())]
        st.session_state["current_chat_index"] = 0

    if "delete_dict" not in st.session_state:
        st.session_state["delete_dict"] = {}
        st.session_state["delete_count"] = 0
        st.session_state["user_input_content"] = ""

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = generate_session_id()
        logger.info(f"Generated new session ID: {st.session_state['session_id']}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Hi, I'm a chatbot who can search the web. How can I help you?",
            }
        ]


# Modern JSON format functions
def load_conversation_history(session_id: str) -> List[Dict[str, Any]]:
    """Load conversation history for a given session ID."""
    file_path = get_history_file_path(session_id)

    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            return history_data.get("messages", [])
    except (json.JSONDecodeError, FileNotFoundError):
        logger.error(f"Failed to load conversation history for session {session_id}")
        return []


def save_conversation_history(
    session_id: str, conversation_id: str, user_input: str, assistant_output: str
) -> None:
    """Save a conversation entry to the history file."""
    file_path = get_history_file_path(session_id)

    # Create a new entry
    new_entry = {
        "id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "input": user_input,
        "output": assistant_output,
    }

    # Load existing history or create new
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                history_data = json.load(f)
        else:
            history_data = {"session_id": session_id, "messages": []}
    except (json.JSONDecodeError, FileNotFoundError):
        history_data = {"session_id": session_id, "messages": []}

    # Add new entry and save
    history_data["messages"].append(new_entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)


def get_all_sessions() -> List[Dict[str, Any]]:
    """Get a list of all available chat sessions."""
    if not os.path.exists(JSON_HISTORY_PATH):
        return []

    sessions = []
    for filename in os.listdir(JSON_HISTORY_PATH):
        if filename.endswith(".json"):
            session_id = filename[:-5]  # Remove .json extension
            try:
                file_path = os.path.join(JSON_HISTORY_PATH, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "messages" in data and data["messages"]:
                        # Get the first message as a title
                        first_message = data["messages"][0]["input"]
                        title = (
                            first_message[:30] + "..."
                            if len(first_message) > 30
                            else first_message
                        )

                        # Get the timestamp of the most recent message
                        latest_timestamp = data["messages"][-1]["timestamp"]

                        sessions.append(
                            {
                                "id": session_id,
                                "title": title,
                                "message_count": len(data["messages"]),
                                "last_updated": latest_timestamp,
                            }
                        )
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                logger.error(f"Error loading session {session_id}: {str(e)}")
                continue

    # Sort by most recent
    sessions.sort(key=lambda x: x["last_updated"], reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a chat session."""
    file_path = get_history_file_path(session_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def rename_session(session_id: str, new_title: str) -> bool:
    """Rename a chat session by adding a title field."""
    file_path = get_history_file_path(session_id)
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # Add or update the title
        history_data["title"] = new_title

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False


def clear_session_history(session_id: str) -> bool:
    """Clear the messages in a session but keep the session."""
    file_path = get_history_file_path(session_id)
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)

        # Keep session metadata but clear messages
        history_data["messages"] = []

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

        return True
    except (json.JSONDecodeError, FileNotFoundError):
        return False


# Legacy format functions
def save_legacy_chat(
    chat_name: str,
    history: List[Dict[str, str]],
    parameters: Dict[str, float],
    context: Dict[str, Any],
) -> None:
    """Save chat data to a legacy format file."""
    file_path = get_legacy_file_path(chat_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {"history": history, "parameters": parameters, "context": context},
            f,
            ensure_ascii=False,
            indent=2,
        )
    logger.info(f"Legacy chat data saved for {chat_name}")


def load_legacy_chat(chat_name: str) -> Dict[str, Any]:
    """Load chat data from a legacy format file."""
    file_path = get_legacy_file_path(chat_name)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"Error parsing JSON in legacy file: {file_path}")

    # Default values
    return {
        "history": [],
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.7,
            "presence_penalty": 0.7,
            "frequency_penalty": 0.7,
        },
        "context": {
            "context_select": "Mặc định",
            "context_input": "",
            "context_level": 3,
        },
    }


def delete_legacy_chat(chat_name: str) -> None:
    """Delete a legacy chat file."""
    file_path = get_legacy_file_path(chat_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Legacy chat file deleted: {chat_name}")


def create_new_chat() -> Tuple[str, str]:
    """Create a new chat and return the chat name and session ID."""
    new_chat_name = "New Chat_" + str(uuid.uuid4())
    session_id = generate_session_id()

    # Initialize empty history for both formats
    save_legacy_chat(
        new_chat_name,
        [],
        {
            "temperature": 0.7,
            "top_p": 0.7,
            "presence_penalty": 0.7,
            "frequency_penalty": 0.7,
        },
        {
            "context_select": "Mặc định",
            "context_input": "",
            "context_level": 3,
        },
    )

    logger.info(f"Created new chat: {new_chat_name} with session ID: {session_id}")
    return new_chat_name, session_id


def rename_chat(old_name: str, new_name: str) -> str:
    """Rename a chat and return the new full chat name."""
    if not new_name:
        return old_name

    new_name = filename_correction(new_name)

    # Create a new name with the same UUID
    uuid_part = old_name.split("_")[-1] if "_" in old_name else str(uuid.uuid4())
    new_chat_name = f"{new_name}_{uuid_part}"

    # Load the old data
    data = load_legacy_chat(old_name)

    # Save with the new name
    save_legacy_chat(
        new_chat_name, data["history"], data["parameters"], data["context"]
    )

    # Delete the old file
    delete_legacy_chat(old_name)

    logger.info(f"Renamed chat from {old_name} to {new_chat_name}")
    return new_chat_name


def get_history_input(
    history: List[Dict[str, str]], context_level: int
) -> List[Dict[str, str]]:
    """Format chat history for API input, considering context level."""
    if not history:
        return []

    # Filter out system messages
    user_assistant_msgs = [msg for msg in history if msg["role"] != "system"]

    # Apply context level
    if context_level > 0 and len(user_assistant_msgs) > context_level * 2:
        # Keep most recent context_level exchanges
        return user_assistant_msgs[-context_level * 2 :]

    return user_assistant_msgs


def download_history(history: List[Dict[str, str]]) -> str:
    """Format chat history for download as markdown."""
    if not history:
        return "# Chat History\n\nNo messages yet."

    result = "# Chat History\n\n"

    for msg in history:
        if msg["role"] == "user":
            result += f"## User\n\n{msg['content']}\n\n"
        elif msg["role"] == "assistant":
            result += f"## Assistant\n\n{msg['content']}\n\n"
        # Skip system messages in the export

    return result


def save_current_chat_data(current_chat: str, new_chat_name: str = None):
    """
    Save the current chat data to file using the legacy format.

    Args:
        current_chat: The name of the current chat session
        new_chat_name: Optional new name for the chat (default: None)
    """
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
