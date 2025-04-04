from typing import Any, Dict, List

import httpx
import streamlit as st


def serper_search(
    query: str, max_results: int = 5, search_type: str = "search"
) -> List[Dict[str, Any]]:
    """
    Perform a search using Serper.dev API via httpx

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        search_type: Type of search - 'search', 'images', 'news', 'places', or 'videos'

    Returns:
        List of dictionaries with keys: title, url, snippet
    """
    # Get API key from Streamlit secrets
    api_key = st.secrets.get("SERPER_API_KEY", None)

    if not api_key:
        st.error(
            "Serper API key not found in secrets. Please add SERPER_API_KEY to your secrets."
        )
        return []

    # Serper API endpoint
    url = f"https://google.serper.dev/{search_type}"

    # Request headers
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    # Request payload
    payload = {
        "q": query,
        # "gl": "us",  # Country to search from
        # "hl": "en",  # Language
        "num": max_results,  # Number of results
    }

    try:
        # Using httpx with a timeout
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Extract organic search results
            results = []

            if search_type == "search":
                organic = data.get("organic", [])
                for item in organic[:max_results]:
                    results.append(
                        {
                            "title": item.get("title", "No title"),
                            "url": item.get("link", "#"),
                            "snippet": item.get("snippet", "No description available."),
                        }
                    )
            elif search_type == "news":
                news = data.get("news", [])
                for item in news[:max_results]:
                    results.append(
                        {
                            "title": item.get("title", "No title"),
                            "url": item.get("link", "#"),
                            "snippet": item.get("snippet", "No description available."),
                            "source": item.get("source", "Unknown source"),
                            "date": item.get("date", "Unknown date"),
                        }
                    )
            elif search_type == "images":
                images = data.get("images", [])
                for item in images[:max_results]:
                    results.append(
                        {
                            "title": item.get("title", "No title"),
                            "url": item.get("link", "#"),
                            "imageUrl": item.get("imageUrl", ""),
                            "source": item.get("source", "Unknown source"),
                        }
                    )
            elif search_type == "places":
                places = data.get("places", [])
                for item in places[:max_results]:
                    results.append(
                        {
                            "title": item.get("title", "No title"),
                            "address": item.get("address", "No address"),
                            "rating": item.get("rating", "No rating"),
                            "reviews": item.get("reviewsCount", "0"),
                        }
                    )

            return results

    except httpx.HTTPError as e:
        st.error(f"HTTP error occurred while searching with Serper: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error occurred while searching with Serper: {str(e)}")
        return []


def format_serper_results(
    results: List[Dict[str, Any]], search_type: str = "search"
) -> str:
    """
    Format Serper search results as a string for display in chat

    Args:
        results: List of search result dictionaries
        search_type: Type of search results to format

    Returns:
        Formatted string with search results
    """
    if not results:
        return "No search results found."

    formatted = f"### Serper {search_type.capitalize()} Results\n\n"

    for i, result in enumerate(results, 1):
        if search_type == "search" or search_type == "news":
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"URL: {result['url']}\n"
            formatted += f"{result['snippet']}\n"

            if search_type == "news":
                formatted += f"Source: {result.get('source', 'Unknown')}, Date: {result.get('date', 'Unknown')}\n"

            formatted += "\n"

        elif search_type == "images":
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"URL: {result['url']}\n"
            formatted += f"Image: {result['imageUrl']}\n"
            formatted += f"Source: {result.get('source', 'Unknown')}\n\n"

        elif search_type == "places":
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"Address: {result['address']}\n"
            formatted += f"Rating: {result.get('rating', 'N/A')} ⭐ ({result.get('reviews', '0')} reviews)\n\n"

    return formatted
