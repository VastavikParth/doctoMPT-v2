# Graph Report - doctoMPT-v2  (2026-11-20)

## Corpus Check
- 66 files · ~59,022 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 3, .example 2, .ico 1)

## Summary
- 449 nodes · 806 edges · 32 communities (17 shown, 15 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `de2cc19d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- next
- consultation.ts
- app/page.tsx
- langgraph_agent.py
- endpoints.py
- save-consultation/route.ts
- DoctoMPT - Dr. DoctoMPT Medical Consultation & Prescription Platform
- backend
- compilerOptions
- records_db.py
- 2. Component-by-Component Deep Dive
- aws-backend-client.ts
- 📡 API Endpoints
- main.py
- security.py
- manifest.json
- not-found.tsx
- SessionMemoryManager
- Neo4jService
- ingest_kaggle_medicines.py
- LangGraphDoctor
- PrescriptionService
- ClinicalRAGChain
- test_api.py
- AGENTS.md
- clinical-consultation-invariants.md
- supabase-emr-invariants.md
- deploy_ec2.sh
- setup_secure_server.sh
- setup_service.sh

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 17 edges
2. `next` - 16 edges
3. `formatErrorMessage()` - 13 edges
4. `getHeaders()` - 12 edges
5. `Home()` - 11 edges
6. `get_connection()` - 11 edges
7. `normalizeMedication()` - 11 edges
8. `getSupabaseAdminClient()` - 10 edges
9. `PrescriptionData` - 10 edges
10. `SessionMemoryManager` - 9 edges

## Surprising Connections (you probably didn't know these)
- `**Hybrid GraphRAG (Graph-Enhanced Vector RAG)**` --references--> `search_1mg()`  [INFERRED]
  README.md → backend/app/services/pharmacy_tools.py
- `**Hybrid GraphRAG (Graph-Enhanced Vector RAG)**` --references--> `search_pharmeasy()`  [INFERRED]
  README.md → backend/app/services/pharmacy_tools.py
- `2.3. FastAPI Core & Security Layer` --references--> `ClinicalRecord`  [INFERRED]
  backend/ARCHITECTURE_DEFENSE.md → lib/aws-backend-client.ts
- `POST()` --calls--> `formatErrorMessage()`  [EXTRACTED]
  app/api/generate-prescription/route.ts → lib/error-utils.ts
- `POST()` --indirect_call--> `normalizeMedication()`  [INFERRED]
  app/api/generate-prescription/route.ts → lib/medication-utils.ts

## Import Cycles
- None detected.

## Communities (32 total, 15 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.06
Nodes (43): eslintConfig, dependencies, jspdf@^4.2.1, lucide-react@^1.74.0, next@16.4.6, react@19.3.0, react-dom@19.3.0, @supabase/supabase-js@^2.119.0 (+35 more)

### Community 1 - "next"
Cohesion: 0.08
Nodes (27): POST(), POST(), SUPPORTED_MIME_TYPES, POST(), SUPPORTED_MIME_TYPES, geistMono, geistSans, metadata (+19 more)

### Community 2 - "consultation.ts"
Cohesion: 0.16
Nodes (23): formattedTranscriptSnippet(), POST(), RecordsPage(), MRS_SAINT_DELAFIELD_BASE64, BRAND_TO_GENERIC_MAP, DRUG_TO_BRAND_MAP, MedicationDirectoryEntry, normalizeMedication() (+15 more)

### Community 3 - "app/page.tsx"
Cohesion: 0.19
Nodes (24): Home(), DoctorAvatar(), DoctorAvatarProps, useGeminiLive(), UseGeminiLiveOptions, checkBackendHealth(), AVAILABLE_VOICES, buildSystemInstructionWithLanguage() (+16 more)

### Community 4 - "langgraph_agent.py"
Cohesion: 0.13
Nodes (3): Settings, Config, AgentState

### Community 5 - "endpoints.py"
Cohesion: 0.17
Nodes (16): chat(), ChatRequest, ChatResponse, delete_consultation_record(), generate_prescription(), get_consultation_record(), list_consultation_records(), list_sqlite_backups() (+8 more)

### Community 6 - "save-consultation/route.ts"
Cohesion: 0.17
Nodes (17): DATA_DIR, DB_FILE, ensureDbFile(), extractClientIp(), GET(), POST(), saveToDb(), DbConsultation (+9 more)

### Community 7 - "DoctoMPT - Dr. DoctoMPT Medical Consultation & Prescription Platform"
Cohesion: 0.11
Nodes (15): search_1mg(), search_local_kaggle_neo4j(), search_pharmeasy(), 1. Frontend Development (Bun Runtime), 2. AWS EC2 Backend (FastAPI + LangGraph + Neo4j), DoctoMPT - Dr. DoctoMPT Medical Consultation & Prescription Platform, 🏗 End-to-End System Architecture, 🚀 Getting Started (+7 more)

### Community 8 - "backend"
Cohesion: 0.10
Nodes (20): build, container_name, depends_on, env_file, environment, ports, restart, container_name (+12 more)

### Community 9 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 10 - "records_db.py"
Cohesion: 0.23
Nodes (8): create_backup(), delete_record_by_id(), get_connection(), get_record_by_id(), get_records(), init_db(), list_backups(), save_record()

### Community 11 - "2. Component-by-Component Deep Dive"
Cohesion: 0.12
Nodes (15): 1. Executive System Architecture, 2.1. Nginx Reverse Proxy & Network Perimeter, 2.2. Uvicorn & Systemd Process Management, 2.4. LangGraph Cyclic StateGraph Engine, 2.5. Neo4j Hybrid GraphRAG (Cloud-Offloaded AuraDB), 2.6. High-Concurrency SQLite EMR Storage (WAL Mode), 2.7. Real-Time Pharmacy APIs (Tata 1mg & PharmEasy), 2. Component-by-Component Deep Dive (+7 more)

### Community 12 - "aws-backend-client.ts"
Cohesion: 0.26
Nodes (13): ChatMessageResponse, deleteClinicalRecord(), fetchClinicalRecordById(), fetchClinicalRecords(), generatePrescription(), getHeaders(), listDatabaseBackups(), saveClinicalRecord() (+5 more)

### Community 13 - "📡 API Endpoints"
Cohesion: 0.17
Nodes (11): 1. Clinical Chat with RAG & Memory, 1. Environment Setup, 2. Run with Docker Compose, 2. Semantic Medicine Search, 3. Ingest Kaggle Indian Medicine Dataset, 3. Reset Session Memory, 4. Health Check, 📡 API Endpoints (+3 more)

### Community 14 - "main.py"
Cohesion: 0.25
Nodes (3): health(), lifespan(), periodic_backup_task()

### Community 16 - "manifest.json"
Cohesion: 0.18
Nodes (10): background_color, description, display, icons, name, orientation, scope, short_name (+2 more)

### Community 17 - "not-found.tsx"
Cohesion: 0.29
Nodes (5): Clinical404Diagnosis, CLINICAL_404_DIAGNOSIS, ClinicalVitals, ClinicWard, executeReloadToMain()

## Knowledge Gaps
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `2.3. FastAPI Core & Security Layer` connect `endpoints.py` to `2. Component-by-Component Deep Dive`?**
  _High betweenness centrality (0.363) - this node is a cross-community bridge._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.05757575757575758 - nodes in this community are weakly interconnected._
- **Why does `ClinicalRecord` connect `endpoints.py` to `aws-backend-client.ts`?**
  _High betweenness centrality (0.338) - this node is a cross-community bridge._
- **Should `next` be split into smaller, more focused modules?**
  _Cohesion score 0.07641196013289037 - nodes in this community are weakly interconnected._
- **Should `langgraph_agent.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `DoctoMPT - Dr. DoctoMPT Medical Consultation & Prescription Platform` be split into smaller, more focused modules?**
  _Cohesion score 0.10822510822510822 - nodes in this community are weakly interconnected._
- **Should `backend` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._