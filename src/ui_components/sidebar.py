import streamlit as st

from src.utils.history_manager import (
    clear_session_history,
)
from src.utils.logger import Logger

logger = Logger("sidebar")


def render_sidebar(
    current_chat, create_chat_callback, delete_chat_callback, reset_chat_name_callback
):
    """
    Render the sidebar with navigation, chat history, and settings.

    Args:
        current_chat: The current chat name
        create_chat_callback: Function to call when creating a new chat
        delete_chat_callback: Function to call when deleting a chat
        reset_chat_name_callback: Function to call when renaming a chat
    """
    with st.sidebar:
        st.title("Navigation")

        # API key input
        if "gemini_api_key" not in st.session_state:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key:
                st.session_state.gemini_api_key = api_key

        # Chat history section
        st.markdown("### Chat History")

        # Create new chat button
        if st.button("✨ New Chat", key="new_chat_btn", use_container_width=True):
            create_chat_callback()
            st.rerun()

        # Display existing chats
        for i, chat in enumerate(st.session_state["history_chats"]):
            chat_name = chat.split("_")[0]

            # Create a container for each chat entry with buttons
            with st.container():
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])

                # Chat selection button
                with col1:
                    if st.button(
                        f"{chat_name}",
                        key=f"history_btn_{i}",
                        use_container_width=True,
                        type=(
                            "secondary"
                            if i == st.session_state["current_chat_index"]
                            else "primary"
                        ),
                    ):
                        st.session_state["current_chat_index"] = i
                        st.rerun()

                # Delete button (only show if more than one chat exists)
                with col2:
                    if len(st.session_state["history_chats"]) > 1:
                        if st.button(
                            "🗑️", key=f"delete_btn_{i}", help="Delete this chat"
                        ):
                            if i == st.session_state["current_chat_index"]:
                                delete_chat_callback()
                                st.rerun()

                # Rename button
                with col3:
                    if st.button("✏️", key=f"rename_btn_{i}", help="Rename this chat"):
                        st.session_state["renaming_chat"] = i

        # Handle chat renaming
        if "renaming_chat" in st.session_state:
            idx = st.session_state["renaming_chat"]
            chat = st.session_state["history_chats"][idx]
            chat_name = chat.split("_")[0]

            new_name = st.text_input(
                "New chat name:", value=chat_name, key=f"rename_input_{idx}"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save", key=f"save_rename_{idx}"):
                    if new_name:
                        if idx == st.session_state["current_chat_index"]:
                            reset_chat_name_callback(new_name)
                        else:
                            # Update the session_state and switch to the renamed chat
                            st.session_state["current_chat_index"] = idx
                            current_chat = st.session_state["history_chats"][idx]
                            reset_chat_name_callback(new_name)

                    # Clear the renaming state
                    del st.session_state["renaming_chat"]
                    st.rerun()

            with col2:
                if st.button("Cancel", key=f"cancel_rename_{idx}"):
                    # Clear the renaming state
                    del st.session_state["renaming_chat"]
                    st.rerun()

        # Model Settings
        st.markdown("---")
        st.markdown("### Model Settings")

        # Model selection
        st.selectbox(
            "Select Model:",
            index=0,
            options=[
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash",
                "gemini-2.0-pro-exp-02-05",
                "gemini-2.0-flash-thinking-exp-01-21",
            ],
            key="select_model",
        )

        # Only show advanced model settings in an expander to save space
        with st.expander("Advanced Model Settings"):
            # Use session_state to store current chat for settings
            # Initialize parameters if not exists
            if "temperature" not in st.session_state:
                st.session_state["temperature"] = 0.7
            if "top_p" not in st.session_state:
                st.session_state["top_p"] = 0.7
            if "presence_penalty" not in st.session_state:
                st.session_state["presence_penalty"] = 0.7
            if "frequency_penalty" not in st.session_state:
                st.session_state["frequency_penalty"] = 0.7
            if "context_level" not in st.session_state:
                st.session_state["context_level"] = 3

            st.slider(
                "Context Level",
                0,
                10,
                st.session_state["context_level"],
                1,
                key="context_level",
                help="Higher values include more chat history but may slow down responses.",
            )

            st.slider(
                "Temperature",
                0.0,
                2.0,
                st.session_state["temperature"],
                0.1,
                key="temperature",
                help="Higher values make output more random, lower values more deterministic.",
            )

            st.slider(
                "Top P",
                0.1,
                1.0,
                st.session_state["top_p"],
                0.1,
                key="top_p",
                help="Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered.",
            )

            st.slider(
                "Presence Penalty",
                -2.0,
                2.0,
                st.session_state["presence_penalty"],
                0.1,
                key="presence_penalty",
                help="Positive values penalize new tokens based on whether they appear in the text so far.",
            )

            st.slider(
                "Frequency Penalty",
                -2.0,
                2.0,
                st.session_state["frequency_penalty"],
                0.1,
                key="frequency_penalty",
                help="Positive values penalize new tokens based on their frequency in the text so far.",
            )

        # Tools
        st.markdown("### Tools")
        if st.button("Clear Chat History", use_container_width=True):
            # Clear current chat history
            st.session_state["history" + current_chat] = []
            # Clear in the new history format if session_id exists
            if "session_id" in st.session_state:
                clear_session_history(st.session_state["session_id"])
            st.rerun()

        # Export chat button
        if st.session_state.get("history" + current_chat):
            pass

            # download_button = st.download_button(
            #     label="Export Chat",
            #     data=download_history(st.session_state["history" + current_chat]),
            #     file_name=f"{current_chat.split('_')[0]}.md",
            #     mime="text/markdown",
            #     use_container_width=True,
            # )

        if st.button("Search Web", use_container_width=True):
            st.switch_page("pages/search.py")

        # Display uploaded files
        st.markdown("### Uploaded Files")

        if (
            "uploaded_file_data" in st.session_state
            and st.session_state.uploaded_file_data
        ):
            for file in st.session_state.uploaded_file_data:
                st.markdown(
                    f"📄 **{file['name']}** ({file['type']}, {file['size']} bytes)"
                )
        else:
            st.info("No files uploaded. Go to the main page to upload files.")
