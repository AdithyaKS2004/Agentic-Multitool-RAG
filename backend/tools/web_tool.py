# backend/tools/web_tool.py

from duckduckgo_search import DDGS

def web_search(query: str, max_results=3):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query)

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