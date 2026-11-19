import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_neo4j import Neo4jVector
from app.core.config import settings

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
        self._driver = None
        self._vector_store = None
        self._embeddings = None

    def get_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
        return self._driver

    def get_embeddings(self):
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.GEMINI_EMBEDDING_MODEL,
                google_api_key=settings.GEMINI_API_KEY
            )
        return self._embeddings

    def init_vector_store(self) -> Optional[Neo4jVector]:
        try:
            embeddings = self.get_embeddings()
            self._vector_store = Neo4jVector.from_existing_graph(
                embedding=embeddings,
                url=self.uri,
                username=self.username,
                password=self.password,
                database=self.database,
                index_name=settings.NEO4J_VECTOR_INDEX_NAME,
                node_label=settings.NEO4J_NODE_LABEL,
                text_node_properties=[
                    "name",
                    "composition",
                    "uses",
                    "side_effects",
                    "manufacturer",
                    "substitute"
                ],
                embedding_node_property=settings.NEO4J_EMBEDDING_PROPERTY,
            )
            return self._vector_store
        except Exception as e:
            logger.warning(f"Could not initialize Neo4j vector store: {e}")
            return None

    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        try:
            if not self._vector_store:
                self.init_vector_store()
            if self._vector_store:
                results = self._vector_store.similarity_search_with_score(query, k=k)
                formatted = []
                for doc, score in results:
                    formatted.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    })
                return formatted
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

        # Fallback to direct Cypher fulltext/fuzzy search if vector index isn't ready
        return self.cypher_search(query, k=k)

    def cypher_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        driver = self.get_driver()
        cypher = """
        MATCH (m:Medicine)
        WHERE toLower(m.name) CONTAINS toLower($q)
           OR toLower(m.composition) CONTAINS toLower($q)
           OR toLower(m.uses) CONTAINS toLower($q)
        RETURN m.name AS name,
               m.composition AS composition,
               m.uses AS uses,
               m.side_effects AS side_effects,
               m.manufacturer AS manufacturer,
               m.substitute AS substitute,
               m.price AS price
        LIMIT $k
        """
        try:
            with driver.session(database=self.database) as session:
                records = session.run(cypher, q=query, k=k)
                results = []
                for rec in records:
                    results.append({
                        "content": f"Medicine: {rec['name']}\nComposition: {rec['composition']}\nUses: {rec['uses']}\nSide Effects: {rec['side_effects']}\nManufacturer: {rec['manufacturer']}\nSubstitutes: {rec['substitute']}\nPrice: {rec['price']}",
                        "metadata": dict(rec),
                        "score": 0.9
                    })
                return results
        except Exception as e:
            logger.error(f"Cypher fallback search failed: {e}")
            return []

    def close(self):
        if self._driver:
            self._driver.close()

neo4j_service = Neo4jService()
