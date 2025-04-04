# Function to call Gemini API with Google Search grounding
import json

import httpx
import streamlit as st

from src.utils.logger import Logger

logger = Logger("chat_grd_w_gg")


def google_grounding_search(client, prompt, history_input=None, api_key=None):
    """
    Call Gemini API with Google Search grounding enabled.

    Args:
        client: OpenAI client (not used but kept for consistent interface)
        prompt (str): The user's query
        history_input: Previous conversation messages (not used by Gemini grounding API)
        api_key (str, optional): Gemini API key. Defaults to None.

    Returns:
        str: The final response text
    """
    if not api_key:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            error_msg = "GEMINI_API_KEY not found in secrets"
            st.error(error_msg)
            return f"Error: {error_msg}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    # Exactly match the payload structure from your working bash command
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }

    headers = {"Content-Type": "application/json"}

    message_placeholder = st.empty()

    try:
        with st.spinner("Searching and grounding with Google..."):
            # Add more debugging info
            logger.info(f"Sending request to Gemini API: {url}")
            logger.info(f"Payload: {json.dumps(payload)}")

            with httpx.Client(timeout=30.0, verify=True) as client:
                response = client.post(url, json=payload, headers=headers)

                # Log the response status and headers
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")

                # Try to get the response text regardless of status
                response_text = response.text
                logger.info(
                    f"Response text: {response_text[:500]}..."
                )  # Truncate if too long

                response.raise_for_status()
                response_json = response.json()

                # Store response for UI components that need it
                st.session_state["grounding_response"] = response_json

                # Extract the main text response
                full_response = ""
                if (
                    "candidates" in response_json
                    and len(response_json["candidates"]) > 0
                ):
                    candidate = response_json["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "text" in part:
                                full_response += part["text"]

                # Display main response text
                message_placeholder.markdown(full_response)

                # Extract and display rendered HTML content if available
                if (
                    "candidates" in response_json
                    and len(response_json["candidates"]) > 0
                    and "groundingMetadata" in response_json["candidates"][0]
                    and "searchEntryPoint"
                    in response_json["candidates"][0]["groundingMetadata"]
                ):
                    rendered_content = response_json["candidates"][0][
                        "groundingMetadata"
                    ]["searchEntryPoint"].get("renderedContent", "")

                    if rendered_content:
                        st.components.v1.html(
                            rendered_content,
                            height=100,
                            scrolling=False,
                        )

                return full_response

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        logger.error(error_msg)
        logger.error(
            f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}"
        )
        st.error(error_msg)
        return f"Error: {error_msg}"
    except httpx.RequestError as e:
        error_msg = f"Request error: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        return f"Error: {error_msg}"
    except json.JSONDecodeError as e:
        error_msg = f"JSON decode error: {e}"
        logger.error(error_msg)
        logger.error(
            f"Raw response: {response_text if 'response_text' in locals() else 'Unknown'}"
        )
        st.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        return f"Error: {error_msg}"
