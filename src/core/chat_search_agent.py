import json
from datetime import datetime

import streamlit as st

from src.utils.logger import Logger
from src.utils.serper_utils import serper_search

logger = Logger("chat_search_agent")

# Define the search tools
SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "serper_search",
            "description": "Search the web for information on a given query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Enhanced query which works properly with web search",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                    },
                    "search_type": {
                        "type": "string",
                        "description": "Type of search to perform",
                        "enum": ["search", "news", "images", "places"],
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]


def chat_with_search(client, prompt, history_input):
    """
    Chat agent that uses web search to find information before responding.

    Args:
        client: OpenAI client instance
        prompt: User's query
        history_input: List of previous messages

    Returns:
        str: The final response text
    """
    # Create a streaming chat completion with tools enabled
    messages = [
        {
            "role": "system",
            "content": "You are Tool Expert. Using Tool always True. Your job is automatically find the best search arguments based on the user query. You must use tools to search the web.",
        }
    ] + [{"role": m["role"], "content": m["content"]} for m in history_input]

    try:
        # Start the streaming completion with tools
        completion = client.chat.completions.create(
            model="qwen2.5-72b-instruct",
            messages=messages,
            tools=SEARCH_TOOLS,
            tool_choice="auto",
            stream=True,
        )

        # Variables for tracking the stream state
        response_messages = []  # For tool responses
        message_placeholder = st.empty()  # For displaying content
        full_response = ""  # Final response accumulator
        tool_call_id = None  # Current tool call ID
        tool_args_json = ""  # Accumulator for tool arguments JSON
        is_tool_call_complete = False  # Flag for completed tool calls

        # Define available search functions
        available_functions = {"serper_search": serper_search}

        # Process the stream
        for chunk in completion:
            logger.info(chunk)
            # Check for regular content
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                message_placeholder.markdown(full_response + "▌")

            # Check for tool calls
            if chunk.choices[0].delta.tool_calls:
                tool_call = chunk.choices[0].delta.tool_calls[0]

                # If this is the start of a tool call, get the ID and function name
                if tool_call.id is not None:
                    tool_call_id = tool_call.id
                    function_name = tool_call.function.name
                    logger.info(
                        f"Starting tool call: {function_name} with ID: {tool_call_id}"
                    )

                # Accumulate the JSON arguments
                if tool_call.function and tool_call.function.arguments:
                    tool_args_json += tool_call.function.arguments
                    logger.info(
                        f"Received tool call arguments fragment: {tool_call.function.arguments}"
                    )

            # Check if the stream is finished or a tool call is complete
            if chunk.choices[0].finish_reason is not None:
                logger.info(
                    f"Stream finished with reason: {chunk.choices[0].finish_reason}"
                )

                # If we have a tool call in progress, execute it
                if tool_args_json and not is_tool_call_complete:
                    with st.spinner("Searching the web...🔍"):
                        try:
                            # Parse the complete JSON arguments
                            func_args = json.loads(tool_args_json)
                            logger.info(f"Received tool call arguments: {func_args}")
                            search_query = func_args.get("query", "Unknown query")
                            logger.info(
                                f"Executing search with query: '{search_query}'"
                            )

                            # Call the search function
                            function_name = (
                                "serper_search"  # Default to this if we don't have it
                            )
                            search_result = available_functions[function_name](
                                **func_args
                            )
                            func_response = json.dumps(search_result)

                            # Add the search results to the message history
                            response_messages.append(
                                {
                                    "role": "function",
                                    "name": function_name,
                                    "content": func_response,
                                }
                            )

                            # Store search info for UI display
                            st.session_state["last_search_query"] = search_query
                            st.session_state["last_search_results"] = search_result
                            st.session_state[
                                "last_search_time"
                            ] = datetime.now().strftime("%H:%M:%S")
                            st.session_state["raw_search_response"] = func_response

                            # Mark as complete to avoid duplicate execution
                            is_tool_call_complete = True

                        except json.JSONDecodeError as e:
                            logger.error(
                                f"JSON decode error in tool call arguments: {e}"
                            )
                            logger.error(f"Partial JSON received: {tool_args_json}")
                        except Exception as e:
                            logger.error(f"Search error: {str(e)}", exc_info=True)
                else:
                    message_placeholder.markdown(full_response)

        # After processing all chunks, use the search results to get a final response
        if is_tool_call_complete and response_messages:
            # Clear previous response
            full_response = ""
            message_placeholder.empty()

            # Create a new completion using the search results
            logger.info(response_messages)
            # Add the original messages plus the function response
            final_messages = [
                {"role": m["role"], "content": m["content"]} for m in history_input
            ]
            final_messages[-1]["content"] = f"Hãy sử dụng thông tin cập nhật từ trên google search để trả lời câu hỏi\n\n\
                Dưới đây là phần thông tin:\n  {response_messages[-1]['content']} \n\n\
                Đây là câu hỏi của người dùng {prompt}"

            # Stream the final response using st.write_stream
            final_stream = client.chat.completions.create(
                model="qwen2.5-72b-instruct",
                messages=final_messages,
                stream=True,
            )

            # Use Streamlit's built-in streaming
            full_response = st.write_stream(final_stream)

        # If we didn't get a complete tool call response
        elif not full_response.strip():
            st.warning("Sorry, I wasn't able to complete the search. Please try again.")
            full_response = (
                "Search operation failed. Please try again with a different query."
            )

        return full_response

    except Exception as e:
        logger.error(f"Error in search agent: {str(e)}", exc_info=True)
        error_message = f"Sorry, an error occurred: {str(e)}"
        st.error(error_message)
        return error_message
