import logging
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.services.neo4j_service import neo4j_service
from app.services.memory_service import memory_manager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DoctoMPT AI, an empathetic, highly knowledgeable clinical AI doctor specializing in primary care and Indian pharmaceutical formulations.

You have access to a verified Indian Medicines Database (Neo4j RAG) containing authentic brand names, chemical compositions/salts, recommended uses, side effects, and Indian market equivalents.

### Instructions:
1. Ground your pharmaceutical advice and suggestions strictly in the provided Context retrieved from the Indian Medicine Database whenever relevant.
2. If citing a medicine, clearly state its generic/active composition (e.g. Paracetamol 500mg, Montelukast + Levocetirizine), primary indications, and common precautions.
3. Be respectful and converse naturally in English or Hinglish depending on what the user speaks.
4. Maintain empathetic, clinical tone with appropriate medical disclaimer: advise consulting a licensed physician before starting prescription medications.
5. In emergencies or severe symptoms (e.g., chest pain, breathing difficulty, acute severe abdominal pain), strongly advise immediate ER visit.

Retrieved Indian Medicine Database Context:
{context}
"""

class ClinicalRAGChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_output_tokens=1024,
        )
        self.output_parser = StrOutputParser()

    async def execute(self, session_id: str, query: str) -> Dict[str, Any]:
        # 1. Retrieve relevant medicines from Neo4j Vector/Graph
        retrieved_docs = neo4j_service.similarity_search(query, k=3)
        context_text = "\n---\n".join([doc["content"] for doc in retrieved_docs]) if retrieved_docs else "No specific medicine records retrieved."

        # 2. Get past conversation history for this session
        history = memory_manager.get_history(session_id)

        # 3. Construct prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])

        chain = prompt | self.llm | self.output_parser

        # 4. Invoke LLM
        response_text = await chain.ainvoke({
            "context": context_text,
            "chat_history": history,
            "question": query,
        })

        # 5. Save turn into memory
        memory_manager.add_user_message(session_id, query)
        memory_manager.add_ai_message(session_id, response_text)

        return {
            "response": response_text,
            "session_id": session_id,
            "retrieved_medicines": retrieved_docs,
        }

rag_chain = ClinicalRAGChain()
