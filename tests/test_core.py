import unittest.mock as mock
from src.core.chat_default import chat_with_default


class MockStream:
    """Mock class for streaming responses"""

    def __init__(self, responses):
        self.responses = responses

    def __iter__(self):
        for response in self.responses:
            yield response


def test_chat_with_default_success():
    """Test successful execution of chat_with_default function"""
    # Mock objects
    mock_client = mock.MagicMock()
    mock_stream = MockStream([{"choices": [{"delta": {"content": "test response"}}]}])
    mock_client.chat.completions.create.return_value = mock_stream

    # Mock streamlit's write_stream
    with mock.patch("streamlit.write_stream", return_value="test response"):
        # Test input
        test_prompt = "Hello"
        test_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        # Call function
        response = chat_with_default(mock_client, test_prompt, test_history)

        # Assertions
        assert response == "test response"
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        assert kwargs["model"] == "qwen2.5-72b-instruct"
        assert kwargs["stream"] is True
        assert len(kwargs["messages"]) == 2


def test_chat_with_default_error():
    """Test error handling in chat_with_default function"""
    # Mock objects
    mock_client = mock.MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("Test error")

    # Mock streamlit's error function
    with mock.patch("streamlit.error"):
        # Test input
        test_prompt = "Hello"
        test_history = [{"role": "user", "content": "Hello"}]

        # Call function
        response = chat_with_default(mock_client, test_prompt, test_history)

        # Assertions
        assert "Sorry, an error occurred: Test error" in response
