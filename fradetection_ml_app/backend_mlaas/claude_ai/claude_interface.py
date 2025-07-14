from langchain_anthropic import ChatAnthropic
from claude_api_key import claude_api_key

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    api_key=claude_api_key
)

response = llm.invoke("Write Python code to clean a CSV into fraud features")
print(response)
