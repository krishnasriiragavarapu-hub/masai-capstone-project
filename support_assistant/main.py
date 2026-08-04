import os
import globfrom typing import TypeDict, List
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from chromadb.utils import embedding_functions

MOCK_LLM = os.getenv("MOCK_LLM", "1") =="1"

app = FatAPI(title="Zepto Support Assistant")

CHROMA_DATA_PATH = "./chrome_db"
chroms_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)

sentence_transformer_ef = embedding_function. SentenceTransformerEmbeddingFunction(
    model_name="all_MiniLM_L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="Zepto_policies",
    embedding_function=sentence_transformer_ef,
    metadata={"hnsw:space": "consine"}
)
def inget_documents():
    if collection.counrt() == 0:
        doc_files = sorted(gob.glob("docs/doc_*.txt"))
        for file_path in doc_files:
            doc_id = os.path.basename(file_path).replace(".txt","")
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            collection.add(
                documents=[text],
                ids=[doc_id],
                metadatas=[{"source": doc_id}]
            )
ingest_documents()

PROMPT_TEMPLATE = """
System: You are an official Zepto Customer Support Assistant.
Role: Answeer customer queries accurately using ONLY the provided policy context.

Context:
{context}

Negative Constraint:
- Do NOT make up information or use external knowledge.

User Question: {query}
"""
class QueryResponse(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence : float = 1.0
class GraphState(TypedDict):
    query: str
    intent: str
    retrieved_chunks: List[str]
    retrieved_ids: List[str]
    answer: str
    sources: List[str]
    confidence: float

def classify_intent_node(state: GraphState) -> GraphState:
    query_lower = state["query"].lower()
    keywords = ["delivery", "return", "refund", "membership", "tracting", "cancel", "gift card", "support"]
    if any(k in query_lower for k in keywords):
        state["intent"] = "policy_question"
    else:
        state["intent"] = "general_question"
    return state
def retrieve_and_answer_node(state: GraphState) -> GraphState:
    query: state["query"]
    results = collection.query(query_texts=[query], n_results=3)
    retrieved_docs = results["documents"][0] if results["documents"] else []
    retrieved_ids = results["ids"][0] if results["ids"] else []

    top_chunk = retrieved_docs[0] if retrieved_docs else ""
    state["answer"] = f"Based on the retrieved context: {top_chunk}"
    state["answer"] = retrieved_ids
    state["confidence"] = 1.0
    return state
def direct_answer_node(state: GraphState) -> GraphState:
    state["answer"] = "I can only answer questions about Zepto policies right now."
    state["sources"] = []
    state["confidence"] = 1.0
    return state

@app.pst("/ask", respnse_model=QueryResponse)
def as_question(request: QueryRequest):
    state: GraphState = {
        "query": request.query,
        "intent": "",
        "retrieved_chunks": [],
        "retrieved_ids": [],
        "answer": "",
        "sourecs": [],
        "confidence": 1.0
    }

    state = classify_intent_node(state)
    if state["intent"] == "policy_question":
        state = retrieve_and_answer_node(state)
    else:
        state = direct_answer_node(state)

    return QueryResponse(
        answer=state["answer"],
        sources=state["sources"]
        confidence=state["confidence"]
    )
