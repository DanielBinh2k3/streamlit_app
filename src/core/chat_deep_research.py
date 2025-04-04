import json

import httpx
import streamlit as st

from src.utils.logger import Logger

logger = Logger("chat_deep_research")


def jina_deepsearch(client, query, conversation_history, api_key=None):
    """
    Call Jina DeepSearch API with Streamlit streaming display.

    Args:
        client: OpenAI client (not used but kept for consistent interface)
        query (str): The user's query
        conversation_history (list): Previous conversation messages
        api_key (str, optional): Jina API key. Defaults to None.

    Returns:
        str: The final complete response text
    """
    if not api_key:
        api_key = st.secrets.get("JINA_API_KEY", "")
        if not api_key:
            error_msg = "JINA_API_KEY not found in secrets"
            st.error(error_msg)
            return f"Error: {error_msg}"

    url = "https://deepsearch.jina.ai/v1/chat/completions"

    messages = conversation_history.copy()
    # Add the current query if it's not the last message
    if not (
        messages and messages[-1]["role"] == "user" and messages[-1]["content"] == query
    ):
        messages.append({"role": "user", "content": query})

    payload = {
        "model": "jina-deepsearch-v1",
        "messages": messages,
        "stream": True,
        "reasoning_effort": "high",
        "max_attempts": 1,
        "no_direct_answer": False,
    }

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    message_placeholder = st.empty()
    thinking_placeholder = st.empty()
    full_response = ""
    thinking_content = ""
    is_thinking = False

    try:
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for chunk in response.iter_lines():
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]  # Remove "data: " prefix
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)

                            # Track search metadata
                            if "visitedURLs" in data:
                                st.session_state["jina_visited_urls"] = data[
                                    "visitedURLs"
                                ]
                            if "readURLs" in data:
                                st.session_state["jina_read_urls"] = data["readURLs"]
                            if "numURLs" in data:
                                st.session_state["jina_num_urls"] = data.get(
                                    "numURLs", 0
                                )

                            # Extract content from the response
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]

                                    # Handle thinking sections
                                    if "<think>" in content:
                                        is_thinking = True
                                        thinking_content = content.split("<think>")[1]
                                        # Show thinking spinner
                                        thinking_placeholder.markdown("🤔 Thinking...")
                                    elif "</think>" in content:
                                        is_thinking = False
                                        # Complete thinking content
                                        thinking_content += content.split("</think>")[0]
                                        # Display thinking section
                                        thinking_section = f"""<details class="thinking-details" open>
                                            <summary>💭 Thinking Process</summary>
                                            <div class="thinking-content">
                                                <div class="thinking-text">{thinking_content}</div>
                                            </div>
                                        </details>"""
                                        full_response += thinking_section
                                        thinking_content = ""
                                        thinking_placeholder.empty()
                                    elif is_thinking:
                                        thinking_content += content
                                        # Update thinking display
                                        thinking_placeholder.markdown(
                                            f"{thinking_content}..."
                                        )
                                    else:
                                        full_response += content

                                    # Update main display
                                    message_placeholder.markdown(
                                        full_response + "▌", unsafe_allow_html=True
                                    )

                        except json.JSONDecodeError:
                            continue

                # Display final response without cursor
                message_placeholder.markdown(full_response, unsafe_allow_html=True)

        return full_response

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error in Jina DeepSearch: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return f"Error: {error_msg}"
    except httpx.RequestError as e:
        error_msg = f"Request error in Jina DeepSearch: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error in Jina DeepSearch: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return f"Error: {error_msg}"
