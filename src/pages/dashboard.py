import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

# Configure page
st.set_page_config(
    page_title="Dashboard | Sunvalue Assistant", page_icon="📊", layout="wide"
)

# CSS for custom styling
css_code = """
.dashboard-card {
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.metric-container {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}
.metric-label {
    font-weight: bold;
}
.metric-value {
    font-size: 1.2rem;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# Main UI Components
st.title("📊 Dashboard")
st.markdown(
    "This dashboard provides analytics and insights about your chat history and usage."
)

# Load chat history data
if "history_chats" in st.session_state and "path" in st.session_state:
    chat_data = []

    for chat_name in st.session_state["history_chats"]:
        file_path = os.path.join(st.session_state["path"], f"{chat_name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Extract basic data
                    name = chat_name.split("_")[0]
                    message_count = len(
                        [
                            msg
                            for msg in data.get("history", [])
                            if msg["role"] in ["user", "assistant"]
                        ]
                    )

                    # Add to our dataset
                    chat_data.append(
                        {
                            "name": name,
                            "message_count": message_count,
                            "last_updated": datetime.fromtimestamp(
                                os.path.getmtime(file_path)
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    # Convert to DataFrame for easier analysis
    if chat_data:
        df_chats = pd.DataFrame(chat_data)

        # Dashboard metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Conversations", len(df_chats))
        with col2:
            st.metric("Total Messages", df_chats["message_count"].sum())
        with col3:
            recent_date = (
                max(df_chats["last_updated"]) if not df_chats.empty else "No data"
            )
            st.metric("Last Activity", recent_date)

        # Charts for analytics
        st.subheader("Conversation Analytics")

        # Most active conversations
        st.markdown("#### Most Active Conversations")

        # Sort by message count and show top 5
        top_conversations = df_chats.sort_values("message_count", ascending=False).head(
            5
        )

        # Create a bar chart
        st.bar_chart(top_conversations.set_index("name")["message_count"])

        # Recent activity
        st.markdown("#### Recent Activity")
        st.dataframe(
            df_chats.sort_values("last_updated", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No chat data available. Start conversations to see analytics.")
else:
    st.info("Dashboard is currently empty. Start some conversations to see data here.")

# Sidebar with settings
with st.sidebar:
    st.title("Dashboard Settings")

    st.markdown("### Navigation")
    if st.button("Back to Chat", use_container_width=True):
        st.switch_page("pages/chat.py")
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("app.py")

    # Refresh data button
    if st.button("Refresh Data", use_container_width=True):
        st.rerun()
