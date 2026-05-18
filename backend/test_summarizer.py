from backend.tools.summarizer_tool import summarizer_tool

response = summarizer_tool(
    "Summarize ovarian cancer detection methods"
)

print("\n====================")
print(response["summary"])
print("====================")