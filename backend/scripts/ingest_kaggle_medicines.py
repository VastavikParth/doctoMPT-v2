import os
import sys
import argparse
import pandas as pd
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.services.neo4j_service import neo4j_service
from langchain_core.documents import Document

def ingest_medicines(csv_path: str, batch_size: int = 50):
    print(f"Reading medicine data from: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records. Columns: {list(df.columns)}")

    # Normalize column names
    col_map = {
        "name": "name",
        "medicine_name": "name",
        "composition": "composition",
        "salts": "composition",
        "uses": "uses",
        "side_effects": "side_effects",
        "sideeffects": "side_effects",
        "manufacturer": "manufacturer",
        "substitute": "substitute",
        "substitutes": "substitute",
        "price": "price",
    }
    
    # Map available columns
    for orig_col in df.columns:
        clean_col = orig_col.strip().lower()
        if clean_col in col_map:
            df.rename(columns={orig_col: col_map[clean_col]}, inplace=True)

    required_cols = ["name", "composition", "uses"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Warning: Expected column '{col}' not found, setting as empty.")
            df[col] = ""

    # Fill NA values
    df = df.fillna("")

    documents: List[Document] = []
    for _, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        comp = str(row.get("composition", "")).strip()
        uses = str(row.get("uses", "")).strip()
        side_effects = str(row.get("side_effects", "")).strip()
        manufacturer = str(row.get("manufacturer", "")).strip()
        substitutes = str(row.get("substitute", "")).strip()
        price = str(row.get("price", "")).strip()

        text_content = (
            f"Brand Name: {name}\n"
            f"Active Composition/Salts: {comp}\n"
            f"Therapeutic Indications/Uses: {uses}\n"
            f"Known Side Effects: {side_effects}\n"
            f"Manufacturer: {manufacturer}\n"
            f"Indian Market Substitutes: {substitutes}\n"
            f"Approximate Price (INR): {price}"
        )

        metadata = {
            "name": name,
            "composition": comp,
            "uses": uses,
            "side_effects": side_effects,
            "manufacturer": manufacturer,
            "substitute": substitutes,
            "price": price,
        }

        documents.append(Document(page_content=text_content, metadata=metadata))

    print(f"Prepared {len(documents)} document chunks for embedding and vector ingestion.")
    
    # Ingest into Neo4j using LangChain Neo4jVector
    try:
        from langchain_neo4j import Neo4jVector
        embeddings = neo4j_service.get_embeddings()

        print(f"Connecting to Neo4j at {settings.NEO4J_URI}...")
        vector_store = Neo4jVector.from_documents(
            documents=documents,
            embedding=embeddings,
            url=settings.NEO4J_URI,
            username=settings.NEO4J_USERNAME,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE,
            index_name=settings.NEO4J_VECTOR_INDEX_NAME,
            node_label=settings.NEO4J_NODE_LABEL,
            text_node_properties=["details", "name", "composition", "uses", "side_effects", "manufacturer", "substitute"],
            embedding_node_property=settings.NEO4J_EMBEDDING_PROPERTY,
        )
        print("Successfully ingested medicine documents into Neo4j Vector Store!")
    except Exception as e:
        print(f"Direct Neo4j Vector Ingestion encountered: {e}")
        print("Falling back to direct Cypher ingestion with metadata...")
        driver = neo4j_service.get_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            for doc in documents:
                session.run("""
                    MERGE (m:Medicine {name: $name})
                    SET m.composition = $composition,
                        m.uses = $uses,
                        m.side_effects = $side_effects,
                        m.manufacturer = $manufacturer,
                        m.substitute = $substitute,
                        m.price = $price,
                        m.details = $details
                """, {
                    **doc.metadata,
                    "details": doc.page_content
                })
        print("Neo4j Cypher node ingestion completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Kaggle Indian Medicines into Neo4j")
    parser.add_argument(
        "--csv",
        type=str,
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_indian_medicines.csv"),
        help="Path to the Indian Medicines CSV dataset",
    )
    args = parser.parse_args()
    ingest_medicines(args.csv)
