import json
from typing import Any, Dict, List

import httpx
import streamlit as st


async def search_duckduckgo_async(
    query: str, max_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Asynchronously search DuckDuckGo using httpx

    Args:
        query: The search query string
        max_results: Maximum number of results to return

    Returns:
        List of search results (each a dict with title, url, and snippet)
    """
    url = "https://api.duckduckgo.com/"

    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract main results
            if data.get("AbstractText"):
                results.append(
                    {
                        "title": data.get("Heading", ""),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("AbstractText", ""),
                    }
                )

            # Extract related topics results
            for topic in data.get("RelatedTopics", [])[: max_results - len(results)]:
                if "Topics" in topic:
                    continue  # Skip nested topics

                results.append(
                    {
                        "title": topic.get("Text", "").split(" - ")[0]
                        if " - " in topic.get("Text", "")
                        else topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    }
                )

                if len(results) >= max_results:
                    break

            return results

    except (httpx.HTTPError, json.JSONDecodeError, KeyError):
        return []


def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for DuckDuckGo search

    Args:
        query: The search query string
        max_results: Maximum number of results to return

    Returns:
        List of search results (each a dict with title, url, and snippet)
    """
    # DuckDuckGo API endpoint for JSON response
    url = "https://api.duckduckgo.com/"

    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    try:
        # Using httpx for the request
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract main results
            if data.get("AbstractText"):
                results.append(
                    {
                        "title": data.get("Heading", ""),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("AbstractText", ""),
                    }
                )

            # Extract related topics results
            for topic in data.get("RelatedTopics", [])[: max_results - len(results)]:
                if "Topics" in topic:
                    continue  # Skip nested topics

                results.append(
                    {
                        "title": topic.get("Text", "").split(" - ")[0]
                        if " - " in topic.get("Text", "")
                        else topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                    }
                )

                if len(results) >= max_results:
                    break

            return results

    except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
        st.error(f"Error performing search: {str(e)}")
        return []


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results as a markdown string

    Args:
        results: List of search result dictionaries

    Returns:
        Formatted markdown string with search results
    """
    if not results:
        return "No results found."

    formatted = "### Search Results\n\n"

    for i, result in enumerate(results, 1):
        formatted += f"**{i}. [{result['title']}]({result['url']})**\n\n"
        formatted += f"{result['snippet']}\n\n"
        formatted += "---\n\n"

    return formatted
