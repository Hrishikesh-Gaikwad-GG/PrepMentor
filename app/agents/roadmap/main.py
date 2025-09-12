from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from typing import List, Optional
from pydantic import BaseModel, Field




from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model = 'gpt-4o-mini', temperature = 0, max_completion_tokens=  1000)


# Build workflow

workflow = StateGraph(StudyPlanState)


workflow.add_node("generate_tentative_plan", generate_tentative_plan)
workflow.add_node("wait_for_approval", wait_for_approval)
workflow.add_node("generate_detailed_plan", generate_detailed_plan)
workflow.add_node("push_to_calendar", push_to_calendar)

workflow.add_edge(START,"generate_tentative_plan")
workflow.add_edge("generate_tentative_plan", "wait_for_approval")
workflow.add_edge("wait_for_approval", "generate_detailed_plan")
workflow.add_edge("generate_detailed_plan", "push_to_calendar")
workflow.add_edge('push_to_calendar', END)

memory = MemorySaver()

app = workflow.compile(checkpointer=memory)

config1 = {'configurable': {'thread_id': '1'}}