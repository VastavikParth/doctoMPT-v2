import json
from typing import Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

PRESCRIPTION_SCHEMA_PROMPT = """You are a senior clinical consultant. Given the patient consultation dialogue, extract and format a structured medical prescription following authentic Indian Medical Council (NMC) standards.

Output strictly valid JSON with this exact schema:
{
  "prescriptionId": "string (e.g. RX-IND-XXXX)",
  "date": "string (YYYY-MM-DD)",
  "patient": {
    "name": "string",
    "age": "string",
    "gender": "string"
  },
  "diagnosis": "string",
  "vitals": {
    "bloodPressure": "string or N/A",
    "temperature": "string or N/A",
    "pulse": "string or N/A",
    "spo2": "string or N/A"
  },
  "medications": [
    {
      "name": "string (Brand and Generic name, e.g. Dolo 650 (Paracetamol 650mg))",
      "dosage": "string (e.g. 1 Tablet)",
      "frequency": "string (e.g. TDS - Thrice daily after meals)",
      "duration": "string (e.g. 3 Days)",
      "instructions": "string (e.g. Take with warm water, avoid empty stomach)"
    }
  ],
  "diagnosticTests": [
    "string (e.g. Complete Blood Count (CBC))"
  ],
  "advice": [
    "string (e.g. Adequate hydration, rest)"
  ],
  "doctor": {
    "name": "Dr. AI Consultation Officer",
    "qualification": "MBBS, MD (General Medicine)",
    "registrationNumber": "MCI-IND-987452"
  }
}
Do not include any markdown backticks around the JSON. Output raw JSON only.
"""

class PrescriptionService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.1,
        )

    async def generate_from_conversation(self, conversation_history: str, patient_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        patient_str = json.dumps(patient_info or {})
        prompt = f"Patient Info: {patient_str}\n\nConsultation Dialogue:\n{conversation_history}\n\nGenerate structured prescription JSON."
        
        response = await self.llm.ainvoke([
            SystemMessage(content=PRESCRIPTION_SCHEMA_PROMPT),
            HumanMessage(content=prompt)
        ])

        raw_text = response.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        try:
            return json.loads(raw_text.strip())
        except Exception:
            return {
                "prescriptionId": "RX-GEN-001",
                "diagnosis": "Clinical Consultation",
                "medications": [],
                "advice": [raw_text]
            }

prescription_service = PrescriptionService()
