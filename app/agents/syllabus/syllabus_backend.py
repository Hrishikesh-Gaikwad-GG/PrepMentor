from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import sqlite3
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages

load_dotenv()

# State
class AgentState(TypedDict):
    query : str
    messages : Annotated[list[BaseMessage], add_messages] 
    syllabus : str
    confirmed : False


#Output_parser_structure
class SyllabusSchema(BaseModel):
    exam_name: str = Field(..., description="Name of the exam")
    topics: list = Field(..., description="topics for the exam")
    subtopics: dict[str, list[str]] = Field(..., description="Detailed subtopics for each topic")


# parser
parser = PydanticOutputParser(pydantic_object= SyllabusSchema)


# prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a task-specific assistant that only provides exam syllabi."),
    ("user", "Generate a detailed syllabus for this exam - {exam}. Return only in structured format."),
    ("assistant", "Use the schema: {format_instructions}")
]).partial(format_instructions=parser.get_format_instructions())


# chatmodel
llm = ChatOpenAI(model = 'gpt-4o-mini', temperature= 0, max_completion_tokens= 2000)


# tools
tavily_tool = TavilySearchResults(k=3)
tools = [tavily_tool]
llm_with_tools = llm.bind_tools(tools)

# Nodes

def fetch_syllabus(state: AgentState):

    query = state["query"]
    message = f"Give me a detailed syallabus for this exam - {query}"
    state['messages'] = HumanMessage(content=message)
    response = llm_with_tools.invoke(message)
    return {"messages": [response]}



def generate_syllabus(state: AgentState):
  
    query = state["query"]
    response = llm.invoke(
        prompt.format(exam=query)
    )
    return {
        "syllabus": response.content,
        "confirmed": False
    }



def confirm_syllabus(state: AgentState):

    print("\n📘 Suggested Syllabus:\n")
    print(state["syllabus"])
    user_input = input("\n✅ Is this syllabus correct? (yes/no): ").strip().lower()
    return {"confirmed": user_input == "yes"}



# tool node
tool_node = ToolNode(tools)

# Initialize the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("fetch_syllabus", fetch_syllabus)
graph.add_node("generate_syllabus", generate_syllabus)
graph.add_node("confirm_syllabus", confirm_syllabus)
graph.add_node('tools', tool_node)

# Define flow
graph.add_edge(START,"fetch_syllabus")

# After fetch, decide if we need to call tools or not
graph.add_conditional_edges(
    "fetch_syllabus",
    tools_condition,  # decides if tool should be used
    {
        "tools": "tools",
        "__end__": "confirm_syllabus"
    }
)
graph.add_edge('tools', 'generate_syllabus')
# After generating syllabus, always go to confirmation
graph.add_edge("generate_syllabus", "confirm_syllabus")

# If user rejects syllabus, loop back to fetch again
graph.add_conditional_edges(
    "confirm_syllabus",
    lambda state: "__end__" if state["confirmed"] else "retry",
    {
        "__end__": END,
        "retry": "fetch_syllabus"
    }
)

# Setup checkpointing (threads)
conn = sqlite3.connect(database = 'chatbot.db', check_same_thread=False)

# Compile graph
checkpointer = SqliteSaver(conn = conn)
app = graph.compile(checkpointer= checkpointer)
