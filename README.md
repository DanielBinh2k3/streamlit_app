# Sunvalue Chatbot ☀️

**A comprehensive, multi-page Streamlit chatbot application featuring advanced AI interaction, integrated web search, persistent history, file handling, and insightful analytics.**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-1.2+-412991.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

Sunvalue Chatbot provides a powerful yet user-friendly interface for interacting with OpenAI's language models. It goes beyond simple Q&A by incorporating DuckDuckGo web search directly into the chat, managing multiple conversation histories, allowing file uploads for context, and offering a dashboard to visualize usage statistics.

<!-- Optional: Add a GIF or screenshot here showcasing the app -->
<!-- ![Sunvalue Chatbot Demo](link_to_your_demo_image_or_gif.gif) -->

## ✨ Key Features

*   **🎈 Multi-Page Interface:**
    *   **🏠 Main Page:** Landing zone with navigation and quick file upload access.
    *   **💬 Chat:** The core interactive chat experience with advanced controls.
    *   **🔍 Search:** A dedicated page for testing and using the DuckDuckGo search functionality.
    *   **📊 Dashboard:** Visual analytics showcasing chat statistics and usage patterns.
*   **🧠 Advanced Chat Capabilities:**
    *   **Multiple Conversations:** Manage and switch between distinct chat sessions.
    *   **Persistent History:** Automatically saves and loads chat history (`history_chats_file/`).
    *   **Context Templates:** Pre-defined prompts to guide conversations for specific tasks.
    *   **Model Parameter Control:** Adjust Temperature, Top-P, Max Tokens, etc., for fine-tuned responses.
    *   **Conversation Management:** Name, load, and manage your chat sessions.
    *   **Export History:** Download chat logs for offline review.
    *   **Context Window Control:** Manage how much history is sent to the API for cost and relevance optimization.
    *   **Streaming Responses:** See model output generated in real-time.
*   **🔍 Integrated Web Search:**
    *   **In-Chat Command:** Use `/search <your query>` directly within the chat interface.
    *   **Dedicated Search Page:** Test search queries independently.
    *   **DuckDuckGo Integration:** Leverages `httpx` for efficient and privacy-respecting web searches.
    *   **Send to Chat:** Easily incorporate search results into your ongoing conversation.
    *   **Robust Error Handling:** Gracefully handles search failures or empty results.
*   **📄 File Handling:**
    *   **Upload Files:** Attach documents or text files relevant to your chat session.
    *   **View Uploads:** Access and review uploaded files directly within the interface.
    *   **Organized Storage:** Files are neatly stored in the `uploads/` directory (automatically created if needed).
*   **🔧 Enhanced UI & Logging:**
    *   **Custom UI Components:** Utilizes custom components (`ui_components/`) for a better user experience.
    *   **JavaScript Enhancements:** Includes JS utilities (`utils/js_utils.py`) for smoother interactions.
    *   **Comprehensive Logging:** Detailed logs are stored in the `logs/` directory for debugging and monitoring.

## 🚀 Getting Started

### Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   An OpenAI API Key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url> # Replace with your actual repo URL
    cd streamlit_app
    ```

2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **OpenAI API Key:** You will be prompted to enter your OpenAI API key directly within the application on any page. This key is stored in Streamlit's session state and is required for chat functionality.
2.  **Directories:** The application will automatically create the following directories if they don't exist:
    *   `history_chats_file/`: Stores saved chat history files (JSON format).
    *   `uploads/`: Stores files uploaded by the user.
    *   `logs/`: Stores application log files.

### Running the Application

1.  **Navigate to the application directory:**
    ```bash
    cd streamlit_app
    ```

2.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

3.  Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

## 🛠️ Usage Guide

1.  **Enter API Key:** Upon first launch or when needed, enter your OpenAI API key in the sidebar input field.
2.  **Start/Load Chat:**
    *   Use the "New Chat" button in the sidebar on the Chat page to start a fresh conversation.
    *   Select a previously saved chat from the dropdown in the sidebar to load its history.
3.  **Interact:** Type your messages in the input box at the bottom of the Chat page.
4.  **Use Search:** Type `/search <your query>` in the chat input to perform a web search. Results will be displayed, and you can choose to send them back into the chat context.
5.  **Upload Files:** Use the file uploader on the Main page or potentially within the Chat page sidebar (depending on final implementation) to add files.
6.  **Adjust Parameters:** Expand the "Parameters" section in the Chat page sidebar to modify model settings like Temperature.
7.  **Explore Pages:** Use the sidebar navigation to switch between the Chat, Search, and Dashboard pages.
8.  **View Analytics:** Navigate to the Dashboard page to see statistics about your chat history.
9.  **Monitor Logs:** Check the `logs/app.log` file for detailed runtime information and potential errors.

## 📁 Project Structure
```
./                            # Project Root
├── .streamlit/            # Config streamlit
│   ├── secrets.toml       # Environment variable
│   ├── config.toml        # StreamLit App setup
├── src/            # Main application source folder
│   ├── app.py                # Main landing page, navigation, core setup
│   ├── pages/                # Streamlit page modules
│   │   ├── 1_💬_Chat.py      # Advanced chat interface with OpenAI & search command
│   │   ├── 2_🔍_Search.py    # Dedicated DuckDuckGo search interface
│   │   └── 3_📊_Dashboard.py # Analytics dashboard for chat history
│   ├── core/                 # Core logic (e.g., API interaction, history management - potentially)
│   ├── ui_components/        # Reusable custom Streamlit UI components
│   ├── utils/                # Utility functions and modules
│   │   ├── helper.py         # General helper functions (chat formatting, file ops)
│   │   ├── ddg_utils.py      # DuckDuckGo search logic using httpx
│   │   └── js_utils.py       # JavaScript snippets for UI enhancements
│   ├── history_chats_file/   # Stores saved chat history JSON files (created automatically)
│   ├── uploads/              # Stores user-uploaded files (created automatically)
│   └── logs/                 # Stores application log files (created automatically)
├── requirements.txt          # Python package dependencies
```

## ⚙️ Dependencies

Key dependencies include:

*   `streamlit`: The core web application framework.
*   `openai`: Official Python client for the OpenAI API.
*   `httpx`: Asynchronous HTTP client used for DuckDuckGo search.
*   `python-dotenv`: For managing environment variables (like API keys).
*   `pandas`, `numpy`, `matplotlib`: For data handling and plotting in the Dashboard.
*   `pillow`: For image handling (potentially used by Streamlit or dashboard).

See `requirements.txt` for the full list of dependencies and specific versions.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](link-to-your-issues-page) (if available) or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information. (You should add a LICENSE file to your repository).
