import os
import sys

import openai
import streamlit as st

sys.path.append(os.getcwd())

from core.chat_deep_research import jina_deepsearch
from core.chat_grd_w_gg import google_grounding_search
from core.chat_search_agent import chat_with_search
from src.ui_components.chat_interface import (
    apply_css_styling,
    clean_thinking_tags,
    render_chat_container,
    render_chat_input,
    render_chat_modes,
    show_chat_history,
    show_search_results,
    stream_chat_message,
)
from src.ui_components.sidebar import render_sidebar
from src.utils.chat_utils import (
    generate_conversation_id,
    prepare_model_input,
    save_current_chat_data,
)
from src.utils.history_manager import (
    create_new_chat,
    delete_legacy_chat,
    delete_session,
    extract_chars,
    initialize_chat_history,
    load_legacy_chat,
    rename_chat,
    rename_session,
    save_conversation_history,
)
from src.utils.logger import Logger
from src.utils.streamlit_utils import (
    apply_js_code,
    initialize_page,
)

logger = Logger("chat")

# Configure page
initialize_page()

# Apply CSS styling from UI components
apply_css_styling()

# Apply custom JavaScript
apply_js_code()

# Call initialization function
initialize_chat_history()

# Get current chat
current_chat = st.session_state["history_chats"][st.session_state["current_chat_index"]]

# Load chat data for current chat
if "history" + current_chat not in st.session_state:
    logger.info(f"Loading chat data for {current_chat}")
    loaded_data = load_legacy_chat(current_chat)
    st.session_state["history" + current_chat] = loaded_data["history"]

    # Initialize parameters and context if not exists
    if "parameters" in loaded_data:
        for key, value in loaded_data["parameters"].items():
            st.session_state[key + current_chat + "value"] = value
    if "context" in loaded_data:
        for key, value in loaded_data["context"].items():
            st.session_state[key + current_chat + "value"] = value


# Function to create a new chat
def create_chat_fun():
    """Create a new chat"""
    new_chat_name, session_id = create_new_chat()

    # Update session state
    st.session_state["history_chats"].append(new_chat_name)
    st.session_state["current_chat_index"] = len(st.session_state["history_chats"]) - 1
    st.session_state["session_id"] = session_id

    # Initialize the history for this chat in session state
    st.session_state["history" + new_chat_name] = []

    # Clear messages loaded flag
    st.session_state.pop("messages_loaded", None)


# Function to delete a chat
def delete_chat_fun():
    """Delete the current chat"""
    if len(st.session_state["history_chats"]) > 1:
        # Delete the chat file
        delete_legacy_chat(current_chat)

        # Also delete in the new history format if session_id exists
        if "session_id" in st.session_state:
            delete_session(st.session_state["session_id"])

        # Remove from the list
        st.session_state["history_chats"].pop(st.session_state["current_chat_index"])

        # Adjust the current index
        if st.session_state["current_chat_index"] >= len(
            st.session_state["history_chats"]
        ):
            st.session_state["current_chat_index"] = (
                len(st.session_state["history_chats"]) - 1
            )

        # Clear the session state for this chat
        for key in list(st.session_state.keys()):
            if current_chat in key:
                del st.session_state[key]


# Function to rename a chat
def reset_chat_name_fun(new_name):
    """Rename the current chat"""
    if not new_name:
        return

    # Use history manager to rename chat
    old_name = current_chat
    new_chat_name = rename_chat(old_name, new_name)

    # Update the list
    st.session_state["history_chats"][st.session_state["current_chat_index"]] = (
        new_chat_name
    )

    # Copy the session state data
    for key in list(st.session_state.keys()):
        if old_name in key:
            new_key = key.replace(old_name, new_chat_name)
            st.session_state[new_key] = st.session_state[key]

    # Also rename in the new history format if session_id exists
    if "session_id" in st.session_state:
        rename_session(st.session_state["session_id"], new_name)


# Main chat interaction function
def process_user_input(prompt):
    """Process user input and generate AI response"""
    try:
        # Display user message immediately in the chat interface
        st.chat_message("user").markdown(prompt)

        # Add user message to history
        st.session_state["history" + current_chat].append({
            "role": "user",
            "content": prompt,
        })

        # Rename chat if first message
        if len(st.session_state["history" + current_chat]) == 1:
            new_name = extract_chars(prompt, 18)
            reset_chat_name_fun(new_name)

        # Get the OpenAI client
        client = openai.OpenAI(
            api_key=st.secrets.get("QWEN_API_KEY", ""),
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )

        # Get chat configuration
        chat_mode = st.session_state.get("selection", "Default")

        # Get model input (history and parameters)
        history_input, parameters = prepare_model_input(current_chat)

        # Process based on chat mode
        full_response = ""

        match chat_mode:
            case "Search-Agent":
                # Create the search agent stream
                messages = [
                    {
                        "role": "system",
                        "content": "You are Tool Expert. Using Tool always True. Your job is automatically find the best search arguments based on the user query. You must use tools to search the web.",
                    }
                ] + [
                    {"role": m["role"], "content": m["content"]} for m in history_input
                ]
                with st.chat_message("assistant"):
                    # Call the search agent function with our streaming chat message
                    full_response = chat_with_search(client, prompt, history_input)
                    show_search_results(
                        st.session_state["last_search_query"],
                        st.session_state["last_search_time"],
                    )
            case "Grounding Truth with Google":
                # Call the Google grounding function inside an assistant message container
                with st.chat_message("assistant"):
                    full_response = google_grounding_search(
                        client, prompt, history_input
                    )

            case "Deep-Research":
                # Call the Jina DeepSearch function inside an assistant message container
                with st.chat_message("assistant"):
                    full_response = jina_deepsearch(client, prompt, history_input)

            case "ReAct-Agent":
                # Create ReAct-Agent prompt
                messages = [
                    {
                        "role": "system",
                        "content": "You are an intelligent agent that follows a thoughtful, step-by-step approach to solving problems.",
                    }
                ] + [
                    {"role": m["role"], "content": m["content"]} for m in history_input
                ]

                # Create a streaming chat completion
                stream = client.chat.completions.create(
                    model="qwen2.5-72b-instruct",
                    messages=messages,
                    stream=True,
                )
                # Stream the response inside a chat message
                full_response = stream_chat_message(stream)

            case _:  # Default case
                # Create a streaming chat completion
                stream = client.chat.completions.create(
                    model="qwen2.5-72b-instruct",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in history_input
                    ],
                    stream=True,
                )
                # Stream the response inside a chat message
                full_response = stream_chat_message(stream)

        # Generate conversation_id
        conversation_id = generate_conversation_id(prompt)

        # Add assistant response to history
        st.session_state["history" + current_chat].append({
            "role": "assistant",
            "content": full_response,
        })

        # Save data in old format
        save_current_chat_data(current_chat)

        # Also save in new JSON format
        save_conversation_history(
            st.session_state["session_id"],
            conversation_id,
            prompt,
            clean_thinking_tags(full_response),
        )

    except Exception as e:
        st.error(f"Error in chat processing: {str(e)}")


# Main app layout
# Render sidebar with callbacks
render_sidebar(current_chat, create_chat_fun, delete_chat_fun, reset_chat_name_fun)

# Main chat container
render_chat_container()

# Display chat modes selection
chat_mode = render_chat_modes()

# Show chat history
show_chat_history(st.session_state["history" + current_chat])


# Display chat input for user
render_chat_input(process_user_input)
