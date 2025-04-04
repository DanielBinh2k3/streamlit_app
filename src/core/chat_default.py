import streamlit as st

from src.utils.logger import Logger

logger = Logger("core")


def chat_with_default(client, prompt, history_input):
    """
    Standard chat without additional tools or specialized capabilities.

    Args:
        client: OpenAI client instance
        prompt: User's query
        history_input: List of previous messages

    Returns:
        full_response: The final text response
    """
    try:
        # Create a streaming chat completion
        stream = client.chat.completions.create(
            model="qwen2.5-72b-instruct",
            messages=[
                {"role": m["role"], "content": m["content"]} for m in history_input
            ],
            stream=True,
        )

        # Display the streaming response using Streamlit's built-in streaming
        full_response = st.write_stream(stream)

        return full_response

    except Exception as e:
        logger.error(f"Error in default chat: {str(e)}", exc_info=True)
        error_message = f"Sorry, an error occurred: {str(e)}"
        st.error(error_message)
        return error_message
