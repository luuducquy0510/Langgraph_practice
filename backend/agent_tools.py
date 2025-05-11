from langchain_community.tools import DuckDuckGoSearchResults
from langchain_experimental.tools import PythonREPLTool


#web search tool
web_search_tool = DuckDuckGoSearchResults(
    max_results=3,
)


# python repl tool
python_repl_tool = PythonREPLTool()