/**
 * Client for DoctoMPT AWS EC2 Backend
 * Connects Next.js frontend with LangGraph + Gemini + Neo4j Vector RAG + 1mg & PharmEasy tools
 */

const AWS_BACKEND_URL =
  process.env.NEXT_PUBLIC_AWS_BACKEND_URL || 'http://16.179.171.132:8000';

export interface ChatMessageResponse {
  response: string;
  session_id: string;
  tools_called: Array<{
    tool: string;
    args: Record<string, any>;
  }>;
  prescription?: Record<string, any>;
}

export async function sendChatMessage(
  message: string,
  sessionId?: string,
  patientInfo?: Record<string, any>
): Promise<ChatMessageResponse> {
  const res = await fetch(`${AWS_BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      patient_info: patientInfo,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`AWS Backend Error (${res.status}): ${errorText}`);
  }

  return res.json();
}

export async function generatePrescription(
  sessionId: string,
  conversationSummary: string,
  patientInfo?: Record<string, any>
) {
  const res = await fetch(`${AWS_BACKEND_URL}/api/prescription/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      conversation_summary: conversationSummary,
      patient_info: patientInfo,
    }),
  });

  if (!res.ok) {
    throw new Error(`Prescription generation failed: ${res.statusText}`);
  }
  return res.json();
}

export async function search1mg(query: string) {
  const res = await fetch(`${AWS_BACKEND_URL}/api/medicines/1mg?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('1mg search failed');
  return res.json();
}

export async function searchPharmEasy(query: string) {
  const res = await fetch(`${AWS_BACKEND_URL}/api/medicines/pharmeasy?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('PharmEasy search failed');
  return res.json();
}

export async function searchKaggleNeo4j(query: string) {
  const res = await fetch(`${AWS_BACKEND_URL}/api/medicines/neo4j?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Neo4j search failed');
  return res.json();
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${AWS_BACKEND_URL}/health`);
    return await res.json();
  } catch (err) {
    return { status: 'offline', error: (err as Error).message };
  }
}
