# Gemini LLM
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
from agent_tools import web_search_tool, python_repl_tool
from schemas import TaskSummarizer, Supervisor
from prompts import task_summarizer_prompt, supervisor_prompt, research_prompt, coder_prompt

from typing import Literal 
from pydantic import BaseModel, Field 
from langchain_core.messages import HumanMessage
from langgraph.types import Command 
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent 


load_dotenv()


os.environ.get("GOOGLE_API_KEY")
llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")


# Task summarizer node

def task_summarizer(state: MessagesState)-> Command[Literal["supervisor"]]:
    system_prompt = task_summarizer_prompt
    messages = [
        {"role": "system", "content": system_prompt},  
    ] + state["messages"] 

    response = llm.with_structured_output(TaskSummarizer).invoke(messages)

    goto = response.next
    reason = response.reason

    # print(f"--- Workflow Transition: tasl_summarizer → {goto.upper()} ---")
    
    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="task_summarizer"),
            ]
        },
        goto=goto, 
    )



def supervisor_node(state: MessagesState) -> Command[Literal["researcher", "coder"]]:

    system_prompt = supervisor_prompt
    
    messages = [
        {"role": "system", "content": system_prompt},  
    ] + state["messages"] 

    response = llm.with_structured_output(Supervisor).invoke(messages)

    goto = response.next
    reason = response.reason

    # print(f"--- Workflow Transition: Supervisor → {goto.upper()} ---")
    
    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto=goto,  
    )


def research_node(state: MessagesState):

    """
        Research agent node that gathers information using Tavily search.
        Takes the current task state, performs relevant research,
        and returns findings for validation.
    """
    
    research_agent = create_react_agent(
        llm,  
        tools=[web_search_tool],  
        state_modifier=research_prompt
    )

    result = research_agent.invoke(state)

    # print(f"--- Workflow Transition: Researcher → end ---")

    return Command(
        update={
            "messages": [ 
                HumanMessage(
                    content=result["messages"][-1].content,  
                    name="researcher"  
                )
            ]
        },
        goto=END, 
    )


def code_node(state: MessagesState):

    code_agent = create_react_agent(
        llm,
        tools=[python_repl_tool],
        state_modifier=coder_prompt
    )

    result = code_agent.invoke(state)

    # print(f"--- Workflow Transition: Coder → end ---")

    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="coder")
            ]
        },
        goto=END,
    )

# build graph

graph = StateGraph(MessagesState)

graph.add_node("task_summarizer", task_summarizer)
graph.add_node("supervisor", supervisor_node) 
graph.add_node("researcher", research_node) 
graph.add_node("coder", code_node) 

graph.add_edge(START, "task_summarizer")  
app = graph.compile()


async def stream_response(user_input: str):
    """
    Stream the response from the app.
    """
    # Initialize the state with the user input
    input = {
        "messages": [user_input]
    }
    events = app.astream_events(input=input, version="v2")

    async for event in events: 
        if event["event"] == "on_chat_model_stream":
            yield event["data"]["chunk"].content
