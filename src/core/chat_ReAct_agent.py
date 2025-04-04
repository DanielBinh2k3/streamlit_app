import streamlit as st

from src.utils.logger import Logger

logger = Logger("chat_react_agent")


def chat_with_react_agent(client, prompt, history_input):
    """
    Chat with a ReAct (Reasoning + Acting) agent that solves problems step-by-step.

    Args:
        client: OpenAI client instance
        prompt: User's query
        history_input: List of previous messages

    Returns:
        full_response: The final text response
    """
    # Create a system prompt that encourages step-by-step reasoning
    messages = [
        {
            "role": "system",
            "content": """You are an intelligent agent that follows a thoughtful, step-by-step approach to solving problems.

1. First, understand the problem completely
2. Break down complex problems into smaller parts
3. Think through each step carefully, considering different approaches
4. Show your reasoning process with clear explanations
5. Arrive at a final answer only after analyzing all relevant aspects

When uncertain, acknowledge limitations and explore alternative approaches.
""",
        }
    ] + [{"role": m["role"], "content": m["content"]} for m in history_input]

    try:
        # Create a streaming chat completion
        stream = client.chat.completions.create(
            model="qwen2.5-72b-instruct",
            messages=messages,
            stream=True,
        )

        # Display the streaming response
        full_response = st.write_stream(stream)

        return full_response

    except Exception as e:
        logger.error(f"Error in ReAct agent: {str(e)}", exc_info=True)
        error_message = f"Sorry, an error occurred: {str(e)}"
        st.error(error_message)
        return error_message
