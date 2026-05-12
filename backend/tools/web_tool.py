'''# backend/tools/web_tool.py

from duckduckgo_search import DDGS
import ssl
import certifi
import requests
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

def web_search(query: str, max_results=3):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query)
            for r in ddgs.text("latest AI news", max_results=3):
                print(r)

            for i, r in enumerate(search_results):
                if i >= max_results:
                    break

                results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "link": r.get("href", "")
                })

    except Exception as e:
        print("Web search failed:", e)

    # 🔁 Fallback if empty
    if not results:
        return fallback_web_results(query)

    return results


def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"

    try:
        response = requests.get(url)
        data = response.json()

        return {
            "heading": data.get("Heading"),
            "abstract": data.get("Abstract"),
            "related": data.get("RelatedTopics", [])[:3]
        }

    except Exception as e:
        return {"error": str(e)}
def fallback_web_results(query):
    return [
        {
            "title": "Web Search Unavailable",
            "body": f"Live web search is currently unavailable. Based on general knowledge, here is some information about: {query}",
            "link": ""
        }
    ]


def format_web_results(results):
    output = ""

    for r in results:
        output += f"{r['title']}\n{r['body']}\n\n"

    return output.strip()
    '''
# backend/tools/web_tool.py
'''
import requests


def web_search(query: str):
    """
    Stable web search using DuckDuckGo Instant API
    """

    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
        data = response.json()

        results = []

        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", ""),
                "body": data.get("Abstract", ""),
                "link": ""
            })

        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict):
                results.append({
                    "title": topic.get("Text", ""),
                    "body": topic.get("Text", ""),
                    "link": topic.get("FirstURL", "")
                })

        return {
            "tool": "web_search",
            "query": query,
            "results": results
        }

    except Exception as e:
        return {
            "tool": "web_search",
            "query": query,
            "error": str(e)
        }
def format_web_results(results: list) -> str:
    """
    Convert web search results into readable text
    """

    if not results:
        return "No web results found."

    formatted = []

    for i, r in enumerate(results):
        title = r.get("title", "")
        body = r.get("body", "")
        link = r.get("link", "")

        entry = f"{i+1}. {title}\n{body}\n{link}"
        formatted.append(entry)

    return "\n\n".join(formatted)
def format_fallback_results(data: dict) -> str:
    """
    Format fallback API response
    """

    if not data:
        return "No fallback results available."

    parts = []

    if data.get("heading"):
        parts.append(f"Heading: {data['heading']}")

    if data.get("abstract"):
        parts.append(f"Summary: {data['abstract']}")

    related = data.get("related", [])

    for i, item in enumerate(related[:3]):
        if isinstance(item, dict):
            text = item.get("Text", "")
            parts.append(f"{i+1}. {text}")

    return "\n".join(parts)
def format_web_output(response: dict) -> str:

    if "results" in response and response["results"]:
        return format_web_results(response["results"])

    elif response.get("abstract") or response.get("related"):
        return format_fallback_results(response)

    elif "error" in response:
        return f"Web search error: {response['error']}"

    return "No useful web information found for this query."
'''

# backend/tools/web_tool.py
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 4) -> dict:
    """
    Searches the web using DuckDuckGo full-text search.
    Returns structured results ready to inject into an LLM prompt.
    """
    try:
        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=max_results))

        results = [
            {
                "title": r.get("title", ""),
                "body":  r.get("body", ""),
                "link":  r.get("href", ""),
            }
            for r in raw
        ]

        return {"tool": "web_search", "query": query, "results": results}

    except Exception as e:
        return {"tool": "web_search", "query": query, "results": [], "error": str(e)}


def format_web_results(search_response: dict) -> str:
    """
    Converts web search results into a plain-text block
    that can be injected directly into the LLM's prompt.
    """
    results = search_response.get("results", [])
    if not results:
        return "Web search returned no results."

    lines = [f"Web search results for: {search_response['query']}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\n{r['body']}\nSource: {r['link']}\n")

    return "\n".join(lines)