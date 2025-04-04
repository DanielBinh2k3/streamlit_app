import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

sys.path.append(os.getcwd())

from utils.ddg_utils import duckduckgo_search
from utils.serper_utils import serper_search

# Configure page
st.set_page_config(
    page_title="Search | Sunvalue Assistant", page_icon="🔍", layout="wide"
)

# CSS for custom styling
css_code = """
<style>
.search-result {
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #f0f8ff;
    border-left: 4px solid #2e86de;
}
.search-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 5px;
}
.search-url {
    color: #2e86de;
    font-size: 0.8rem;
    margin-bottom: 10px;
}
.search-snippet {
    font-size: 0.9rem;
}
.search-image {
    max-width: 200px;
    max-height: 200px;
    margin-top: 10px;
}
.search-news {
    background-color: #e6f7ff;
    border-left: 4px solid #1890ff;
}
.search-place {
    background-color: #f6ffed;
    border-left: 4px solid #52c41a;
}
</style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# Initialize session state for search history
if "search_history" not in st.session_state:
    st.session_state.search_history = []


def add_to_search_history(
    query: str, results: List[Dict[str, Any]], search_type: str, engine: str
):
    """Add a search query and results to history"""
    if query and results:
        # Limit history to last 10 searches
        if len(st.session_state.search_history) >= 10:
            st.session_state.search_history.pop(0)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.search_history.append({
            "timestamp": timestamp,
            "query": query,
            "results": results,
            "search_type": search_type,
            "engine": engine,
        })


def perform_search(
    query: str,
    max_results: int = 5,
    engine: str = "duckduckgo",
    search_type: str = "search",
) -> List[Dict[str, Any]]:
    """Perform a search using the selected engine"""
    with st.spinner(f"Searching for '{query}' using {engine}..."):
        if engine == "duckduckgo":
            return duckduckgo_search(query, max_results=max_results)
        elif engine == "serper":
            return serper_search(
                query, max_results=max_results, search_type=search_type
            )
        else:
            st.error(f"Unknown search engine: {engine}")
            return []


def display_search_results(results: List[Dict[str, Any]], search_type: str = "search"):
    """Display search results in a custom format"""
    if not results:
        st.error("No results found. Please try a different query.")
        return

    for result in results:
        if search_type == "search" or search_type == "news":
            css_class = (
                "search-result"
                if search_type == "search"
                else "search-result search-news"
            )
            with st.container():
                st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='search-title'>{result['title']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='search-url'><a href='{result['url']}' target='_blank'>{result['url']}</a></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='search-snippet'>{result['snippet']}</div>",
                    unsafe_allow_html=True,
                )

                if search_type == "news" and "date" in result:
                    st.markdown(
                        f"<div class='search-date'>📅 {result.get('date', 'Unknown')} | 📰 {result.get('source', 'Unknown')}</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

        elif search_type == "images":
            with st.container():
                st.markdown("<div class='search-result'>", unsafe_allow_html=True)
                st.markdown(
                    f"<div class='search-title'>{result['title']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='search-url'><a href='{result['url']}' target='_blank'>{result['url']}</a></div>",
                    unsafe_allow_html=True,
                )

                if "imageUrl" in result and result["imageUrl"]:
                    st.markdown(
                        f"<img src='{result['imageUrl']}' class='search-image' />",
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)

        elif search_type == "places":
            with st.container():
                st.markdown(
                    "<div class='search-result search-place'>", unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='search-title'>{result['title']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='search-snippet'>📍 {result.get('address', 'No address')}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='search-snippet'>⭐ {result.get('rating', 'N/A')} ({result.get('reviews', '0')} reviews)</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)


# Main UI Components
st.title("🔍 Search")
st.markdown(
    "Use this page to search the web using DuckDuckGo or Serper.dev (Google results)."
)

# Simplified sidebar with only essential navigation
with st.sidebar:
    st.title("Navigation")

    # Add simple navigation buttons
    if st.button("Back to Chat", use_container_width=True):
        st.switch_page("pages/chat.py")
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("app.py")

    # API key status check without modifying any state
    if "SERPER_API_KEY" in st.secrets:
        st.success("Serper API Key is configured")

# Top navigation buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Clear Search", use_container_width=True):
        # Create a separate function for callback
        def clear_search():
            if "search_query" in st.session_state:
                del st.session_state["search_query"]

        clear_search()
        st.rerun()

with col2:
    if st.button("Clear History", use_container_width=True):
        st.session_state.search_history = []
        st.rerun()


# Search form
with st.form("search_form"):
    # Search query and max results
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Enter search query:",
            value=st.session_state.get("search_query", ""),
            placeholder="Type your search query...",
            key="form_search_query",
        )
    with col2:
        max_results = st.selectbox(
            "Results:", options=[3, 5, 10, 15], index=1, key="form_max_results"
        )

    # Engine selection
    col3, col4 = st.columns(2)
    with col3:
        engine_options = ["duckduckgo", "serper"]
        default_engine = st.session_state.get("engine_selection", "duckduckgo")
        engine_index = (
            engine_options.index(default_engine)
            if default_engine in engine_options
            else 0
        )

        search_engine = st.selectbox(
            "Search Engine:",
            options=engine_options,
            index=engine_index,
            key="form_engine",
        )

    with col4:
        # Only show search type for Serper
        if search_engine == "serper":
            type_options = ["search", "news", "images", "places"]
            default_type = st.session_state.get("type_selection", "search")
            type_index = (
                type_options.index(default_type) if default_type in type_options else 0
            )

            search_type = st.selectbox(
                "Search Type:", options=type_options, index=type_index, key="form_type"
            )
        else:
            search_type = "search"

    # Submit button
    submitted = st.form_submit_button("Search", use_container_width=True)

    if submitted and search_query:
        # Store as temporary variables first without setting session state directly
        st.session_state["temp_query"] = search_query
        st.session_state["temp_max_results"] = max_results
        st.session_state["temp_engine"] = search_engine
        st.session_state["temp_type"] = search_type

        # Update UI defaults for next time form loads
        st.session_state["engine_selection"] = search_engine
        st.session_state["type_selection"] = search_type

        # Trigger a rerun to apply these changes
        st.rerun()

# Process search if temp query exists
if "temp_query" in st.session_state:
    query = st.session_state.pop("temp_query")
    max_results = st.session_state.pop("temp_max_results", 5)
    engine = st.session_state.pop("temp_engine", "duckduckgo")
    search_type = st.session_state.pop("temp_type", "search")

    # Store the current query for display purposes
    st.session_state["search_query"] = query

    # Perform search
    results = perform_search(
        query, max_results=max_results, engine=engine, search_type=search_type
    )

    # Add to history
    add_to_search_history(query, results, search_type, engine)

    # Display results
    st.subheader(f"Results for '{query}' using {engine.capitalize()} ({search_type})")
    display_search_results(results, search_type)
# Show recent searches
if st.session_state.search_history:
    with st.expander("Recent Searches", expanded=False):
        for i, search in enumerate(reversed(st.session_state.search_history)):
            engine_icon = "🦆" if search["engine"] == "duckduckgo" else "🔍"
            history_label = f"{engine_icon} {search['query']}"

            if st.button(history_label, key=f"history_{i}"):
                # Use temporary variables to avoid widget key conflicts
                st.session_state["temp_query"] = search["query"]
                st.session_state["temp_engine"] = search["engine"]
                st.session_state["temp_type"] = search.get("search_type", "search")
                st.session_state["temp_max_results"] = 5
                st.rerun()
