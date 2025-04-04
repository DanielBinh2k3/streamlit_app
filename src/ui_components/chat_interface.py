import json
from typing import Any, Callable, Dict, List

import streamlit as st


def parse_thinking_content(content: str) -> str:
    """Parse content to handle thinking sections from model output."""
    if not content or ("<think>" not in content or "</think>" not in content):
        return content

    try:
        parts = content.split("</think>")
        if len(parts) > 1:
            pre_think = parts[0].split("<think>")[0].strip()
            post_think = parts[1].strip()
            thinking_content = parts[0].split("<think>")[1].strip()

            # Format thinking section
            thinking_section = f"""<details class="thinking-details">
                <summary>💭 Thinking Process</summary>
                <div class="thinking-content">
                    <div class="thinking-text">{thinking_content}</div>
                </div>
            </details>"""

            # Combine parts with proper spacing
            if pre_think and post_think:
                return f"{pre_think}\n\n{thinking_section}\n\n{post_think}"
            elif pre_think:
                return f"{pre_think}\n\n{thinking_section}"
            elif post_think:
                return f"{thinking_section}\n\n{post_think}"
            else:
                return thinking_section
    except Exception as e:
        st.error(f"Error parsing thinking content: {str(e)}")
        return content

    return content


def clean_thinking_tags(content: str) -> str:
    """Clean <think> tags from content when we need just the final output."""
    if not content:
        return ""

    if "<think>" in content:
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        else:
            content = content.split("<think>")[0].strip()
    return content


def show_chat_message(message: Dict[str, str]) -> None:
    """Display a single chat message with appropriate styling."""
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            # Parse thinking content before displaying
            content = parse_thinking_content(message["content"])
            st.markdown(content, unsafe_allow_html=True)


def show_chat_history(chat_history: List[Dict[str, str]]) -> None:
    """Display all messages in the chat history."""
    if not chat_history:
        return

    for message in chat_history:
        show_chat_message(message)


def render_chat_container(title: str = "💬 Chat") -> None:
    """Render the main chat container with title."""
    st.title(title)

    # You could add a description or help text here
    # st.info("Type a message below to start chatting with the assistant.")


def render_chat_modes() -> str:
    """
    Render the chat mode selection UI.

    Returns:
        str: The selected chat mode
    """
    # Create a mapping of options to icons
    option_map = {
        "Default": "💬",
        "Search-Agent": "🔍",
        "Grounding Truth with Google": "🌐",
        "Deep-Research": "🔍🧠🌐",
        "ReAct-Agent": "🧠",
    }

    # Use segmented control for selecting chat mode
    selection = st.segmented_control(
        "Select chat mode:",
        options=option_map.keys(),
        format_func=lambda option: f"{option_map[option]} {option}",
        selection_mode="single",
        key="selection",
    )

    # Show description based on selected mode
    if selection == "Search-Agent":
        st.caption("Uses **web search** to find information before responding")
    elif selection == "Grounding Truth with Google":
        st.caption("Uses **Google search API** for real-time information")
    elif selection == "Deep-Research":
        st.caption("Performs in-depth research with **Jina DeepSearch**")
    elif selection == "ReAct-Agent":
        st.caption("Uses **step-by-step reasoning** approach")
    else:
        st.caption("**Standard chat** without additional tools")

    return selection


def render_chat_input(
    on_submit: Callable[[str], None], placeholder: str = "Ask something..."
) -> None:
    """
    Render the chat input box.

    Args:
        on_submit: Callback function to call when a message is submitted
        placeholder: Placeholder text for the input box
    """
    if prompt := st.chat_input(placeholder):
        on_submit(prompt)


def apply_css_styling() -> None:
    """Apply CSS styling for chat interface."""
    css_code = """
    <style>
    .user-message {
        background-color: #f0f2f6;
    }
    .assistant-message {
        background-color: #e6f3ff;
    }
    .delete-message-button {
        float: right;
        color: #ff4b4b;
        cursor: pointer;
    }

    /* Thinking process styling */
    .thinking-details {
        margin: 0.75em 0;
        padding: 0.25em;
        border-radius: 4px;
        background-color: #f5f7f9;
        border: 1px solid #e0e0e0;
    }

    .thinking-content {
        margin: 0.5em 0;
        padding: 0.75em;
        background-color: #f8f9fa;
        border-radius: 4px;
        border-left: 3px solid #1E88E5;
    }

    .thinking-text {
        white-space: pre-wrap;
        word-wrap: break-word;
        overflow-wrap: break-word;
        font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
        font-size: 0.9em;
        line-height: 1.4;
        color: #333;
    }

    details > summary {
        cursor: pointer;
        padding: 0.3em 0.5em;
        border-radius: 4px;
        font-weight: 500;
        color: #1E88E5;
        font-size: 0.9em;
    }

    details > summary:hover {
        background-color: #e9ecef;
    }

    details[open] > summary {
        margin-bottom: 0.4em;
        border-bottom: 1px solid #eaecef;
    }
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)


def stream_chat_message(stream: Any) -> str:
    """
    Stream a chat message within the assistant's chat message container.

    Args:
        stream: A stream from OpenAI's API

    Returns:
        str: The complete response text
    """
    # Create a chat message container for the assistant
    with st.chat_message("assistant"):
        # Use Streamlit's streaming feature to update content in real-time
        response = st.write_stream(stream)

    return response


def show_search_results(search_query: str, search_time: str) -> None:
    """Display search results in an expander."""
    if "last_search_results" in st.session_state:
        with st.expander(f"🔍 Search performed: '{search_query}'", expanded=False):
            st.markdown(f"**Time:** {search_time}")

            # Add timing information to the display
            if "operation_times" in st.session_state:
                st.markdown("**Performance:**")
                for op, seconds in st.session_state["operation_times"].items():
                    st.markdown(f"- {op}: {seconds:.2f} seconds")

            # Use tabs for better organization
            tab1, tab2 = st.tabs(["Formatted Results", "Raw JSON"])

            with tab1:
                # Display search results in a more readable format
                results = st.session_state["last_search_results"]
                raw_response = st.session_state.get("raw_search_response", "")

                # Format and display search results
                st.markdown("### Search Results")

                try:
                    # Try to parse raw_response if it's a string
                    if isinstance(raw_response, str):
                        parsed_results = json.loads(raw_response)
                    else:
                        parsed_results = results

                    # Display results with proper formatting
                    if "organic" in parsed_results:
                        # Handle serper.dev format
                        for idx, result in enumerate(parsed_results["organic"][:5], 1):
                            title = result.get("title", "No title")
                            url = result.get("link", "#")
                            snippet = result.get("snippet", "No description")

                            st.markdown(f"**{idx}. [{title}]({url})**")
                            st.markdown(f"{snippet}")
                            st.markdown("---")
                    elif isinstance(parsed_results, list):
                        # Handle list format
                        for idx, result in enumerate(parsed_results[:5], 1):
                            title = result.get("title", "No title")
                            url = result.get("url", result.get("link", "#"))
                            snippet = result.get(
                                "snippet",
                                result.get("description", "No description"),
                            )

                            st.markdown(f"**{idx}. [{title}]({url})**")
                            st.markdown(f"{snippet}")
                            st.markdown("---")
                    else:
                        st.info(
                            "No search results found or results in unexpected format."
                        )
                except Exception as e:
                    st.error(f"Error displaying search results: {str(e)}")
                    st.json(results)

            with tab2:
                # Show raw JSON for debugging/advanced users
                if "raw_search_response" in st.session_state:
                    st.code(st.session_state["raw_search_response"], language="json")
