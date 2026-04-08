from app.agents.tools.db_search import search_knowledge_base
from app.agents.tools.web_search import web_search
from app.agents.graph.stage import AgentState
from app.agents.nodes.psychoeducation_node import psychoeducation_node
from app.agents.nodes.message_classification import message_classification_node
from app.agents.nodes.crisis_protocol_node import crisis_protocol_node
from app.agents.nodes.empathy_node import empathy_node
from app.agents.nodes.safety_checker_node import safety_checker_node
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import START, END, StateGraph
from typing import Literal

from app.agents.graph.stage import AgentState

def route_by_risk(state: AgentState):
    """
    Hàm đọc risk_level từ state để quyết định luồng đi.
    Bắt buộc phải trả về chuỗi String là tên của Node đích.
    """
    risk = state.get("risk_level", "normal")
    
    if risk == "high":
        return "crisis_protocol"    
    else:
        return "message_classification"

def route_by_message(state:AgentState):
    query_type = state.get("query_type", "general")

    if query_type == "general":
        return "empathy"
    else:
        return "psychoeducation"

def route_after_agent(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "__end__"

tools = [web_search, search_knowledge_base]
tools_node = ToolNode(tools)

workflow = StateGraph(AgentState)
workflow.add_node("psychoeducation", psychoeducation_node)
workflow.add_node("tools", tools_node)
workflow.add_node("message_classification", message_classification_node)
workflow.add_node("crisis_protocol", crisis_protocol_node)
workflow.add_node("empathy", empathy_node)
workflow.add_node("safety_checker", safety_checker_node)

workflow.add_edge(START, "safety_checker")
workflow.add_conditional_edges(
    "safety_checker",
    route_by_risk
)
workflow.add_edge("crisis_protocol", END)
workflow.add_conditional_edges(
    "message_classification",
    route_by_message
)

workflow.add_conditional_edges(
    "empathy",
    route_after_agent
)
workflow.add_conditional_edges(
    "psychoeducation",
    route_after_agent
)

def route_after_tools(state: AgentState) -> str:
    messages = state["messages"]
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            if state.get("query_type", "general") == "general":
                return "empathy"
            else:
                return "psychoeducation"
    
    return "psychoeducation" # Default fallback

workflow.add_conditional_edges(
    "tools",
    route_after_tools
)

graph = workflow.compile()
