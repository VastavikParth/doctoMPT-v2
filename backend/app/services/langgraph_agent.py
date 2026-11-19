import logging
from typing import Annotated, Sequence, TypedDict, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings
from app.services.pharmacy_tools import PHARMACY_TOOLS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DoctoMPT AI, an expert, empathetic clinical AI Doctor operating in India.
You converse fluently in English and Hinglish.

You have access to live Indian pharmaceutical tools:
1. `search_1mg`: Real-time Tata 1mg medicine details, active salts, packaging, manufacturers, and price.
2. `search_pharmeasy`: Real-time PharmEasy search for Indian market availability, alternatives, and formulations.
3. `search_local_kaggle_neo4j`: Local Neo4j Knowledge Graph & Vector DB loaded from Kaggle Indian medicines data (uses, side-effects, compositions).

### Clinical Guidelines:
- Ground all recommendations in verified Indian pharmaceutical brands and generic salts.
- If the patient mentions symptoms, query your tools to find authentic Indian brands and correct active molecules.
- Maintain a warm, reassuring doctor demeanor.
- If symptoms indicate an emergency (e.g. chest pain, severe dyspnea, acute trauma), clearly instruct the patient to visit the nearest emergency room immediately.
- When sufficient clinical information has been gathered, you can outline a structured prescription recommendation.
"""

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    session_id: str
    patient_info: Optional[Dict[str, Any]]
    prescription: Optional[Dict[str, Any]]

class LangGraphDoctor:
    def __init__(self):
        # Initialize Gemini 1.5 Flash with tool calling support
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.2,
        )
        self.llm_with_tools = self.llm.bind_tools(PHARMACY_TOOLS)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 1. Define Nodes
        def call_model(state: AgentState):
            messages = state["messages"]
            if not any(isinstance(m, SystemMessage) for m in messages):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        tool_node = ToolNode(PHARMACY_TOOLS)

        workflow.add_node("doctor_agent", call_model)
        workflow.add_node("tools", tool_node)

        # 2. Define Edges
        workflow.set_entry_point("doctor_agent")

        workflow.add_conditional_edges(
            "doctor_agent",
            tools_condition,
            {
                "tools": "tools",
                END: END,
            }
        )
        workflow.add_edge("tools", "doctor_agent")

        return workflow.compile(checkpointer=self.memory)

    async def chat(self, session_id: str, message: str, patient_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {"configurable": {"thread_id": session_id}}
        
        initial_input = {
            "messages": [HumanMessage(content=message)],
            "session_id": session_id,
            "patient_info": patient_info or {},
        }

        # Run through the compiled LangGraph
        result = await self.graph.ainvoke(initial_input, config=config)
        
        # Get the latest AI response message
        last_message = result["messages"][-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

        # Check if any tools were called
        tools_called = []
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tools_called.append({
                        "tool": tc.get("name"),
                        "args": tc.get("args")
                    })

        return {
            "response": response_text,
            "session_id": session_id,
            "tools_called": tools_called,
            "patient_info": result.get("patient_info"),
            "prescription": result.get("prescription"),
        }

langgraph_doctor = LangGraphDoctor()
