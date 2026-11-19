from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from app.services.langgraph_agent import langgraph_doctor
from app.services.prescription_service import prescription_service
from app.services.pharmacy_tools import search_1mg, search_pharmeasy, search_local_kaggle_neo4j

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., description="Patient dialogue or medical query")
    session_id: Optional[str] = Field(None, description="Unique session thread ID for LangGraph state persistence")
    patient_info: Optional[Dict[str, Any]] = Field(default=None, description="Patient vitals, name, age, gender")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_called: List[Dict[str, Any]]
    prescription: Optional[Dict[str, Any]] = None

class PrescriptionRequest(BaseModel):
    session_id: str
    conversation_summary: str
    patient_info: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    try:
        result = await langgraph_doctor.chat(
            session_id=session_id,
            message=request.message,
            patient_info=request.patient_info
        )
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            tools_called=result.get("tools_called", []),
            prescription=result.get("prescription")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangGraph Agent Error: {str(e)}")

@router.post("/prescription/generate")
async def generate_prescription(request: PrescriptionRequest):
    try:
        prescription = await prescription_service.generate_from_conversation(
            conversation_history=request.conversation_summary,
            patient_info=request.patient_info
        )
        return {"status": "success", "prescription": prescription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prescription generation error: {str(e)}")

@router.get("/medicines/1mg")
def query_1mg(q: str = Query(..., description="Search 1mg for Indian medicines")):
    try:
        return {"source": "Tata 1mg", "query": q, "results": search_1mg.invoke(q)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicines/pharmeasy")
def query_pharmeasy(q: str = Query(..., description="Search PharmEasy for Indian medicines")):
    try:
        return {"source": "PharmEasy", "query": q, "results": search_pharmeasy.invoke(q)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicines/neo4j")
def query_neo4j(q: str = Query(..., description="Search local Neo4j Kaggle vector store")):
    try:
        return {"source": "Neo4j Kaggle RAG", "query": q, "results": search_local_kaggle_neo4j.invoke(q)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
