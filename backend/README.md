# DoctoMPT AWS Backend: LangGraph + Gemini 3.5 Flash LITE + Neo4j Hybrid GraphRAG

This service runs on AWS EC2 and handles clinical reasoning, conversational memory, live pharmacy tools (Tata 1mg & PharmEasy), and Retrieval-Augmented Generation (RAG) over Indian pharmaceutical data from Kaggle using Neo4j and Google Gemini 3.5 Flash LITE.

---

## 🏗 Architecture
- **Framework:** FastAPI (Python 3.11)
- **Orchestration:** LangGraph (`langgraph`, `langchain-google-genai`, `langchain-neo4j`)
- **Reasoning LLM:** Google Gemini 3.5 Flash LITE (`gemini-3.5-flash-lite`)
- **Spoken Consultation Model:** Google Gemini 3.8 Flash LIVE (`gemini-3.8-flash-live`)
- **Embeddings:** Google `text-embedding-004`
- **Vector & Graph DB:** Neo4j 5 (Vector Indexing + Graph relationships)
- **Tools:** Real-time Tata 1mg & PharmEasy live inventory and pricing
- **Dataset:** Kaggle Indian Medicines Dataset (salts, compositions, uses, side effects, manufacturers, substitutes, price)
- **Memory:** LangGraph `MemorySaver` thread state checkpointing

---

## 🚀 Quick Start (Local or EC2)

### 1. Environment Setup
```bash
cd backend
cp .env.example .env
# Ensure GEMINI_API_KEY and NEO4J credentials are set
```

### 2. Run with Docker Compose
```bash
docker compose up -d --build
```

### 3. Ingest Kaggle Indian Medicine Dataset
```bash
# Ingest default sample or your downloaded Kaggle CSV
python scripts/ingest_kaggle_medicines.py --csv data/sample_indian_medicines.csv
```

---

## 📡 API Endpoints

### 1. Clinical Chat with RAG & Memory
`POST /api/chat`
```json
{
  "message": "I have headache and fever, can I take Dolo 650 or Calpol?",
  "session_id": "optional-uuid-string"
}
```
**Response:**
```json
{
  "response": "Clinical guidance grounded in verified Indian medicine data...",
  "session_id": "c1f7b7e2-...",
  "retrieved_medicines": [ ... ]
}
```

### 2. Semantic Medicine Search
`GET /api/medicines/search?q=Paracetamol&limit=5`

### 3. Reset Session Memory
`POST /api/chat/reset`
```json
{
  "session_id": "c1f7b7e2-..."
}
```

### 4. Health Check
`GET /health`
