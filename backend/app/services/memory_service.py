from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class SessionMemoryManager:
    """
    Manages in-memory multi-turn conversational history per session.
    Keeps sliding window of recent clinical dialogue exchanges.
    """
    def __init__(self, max_history: int = 12):
        self.max_history = max_history
        self._sessions: Dict[str, List[BaseMessage]] = {}

    def get_history(self, session_id: str) -> List[BaseMessage]:
        return self._sessions.get(session_id, [])

    def add_user_message(self, session_id: str, message: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(HumanMessage(content=message))
        self._trim(session_id)

    def add_ai_message(self, session_id: str, message: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(AIMessage(content=message))
        self._trim(session_id)

    def clear(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _trim(self, session_id: str):
        if len(self._sessions[session_id]) > self.max_history:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history:]

    def format_history_as_text(self, session_id: str) -> str:
        messages = self.get_history(session_id)
        formatted = []
        for msg in messages:
            role = "Patient" if isinstance(msg, HumanMessage) else "Doctor"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)

memory_manager = SessionMemoryManager()
