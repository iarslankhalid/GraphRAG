"""
Pydantic models for API request/response validation.
Defines the contract between frontend and backend.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    document_id: int
    filename: str
    entities_extracted: int
    relationships_extracted: int
    chunks_created: int
    message: str


class DocumentInfo(BaseModel):
    """Document metadata."""
    id: int
    filename: str
    content: str
    upload_date: str
    file_type: str


class EntityNode(BaseModel):
    """Graph entity node."""
    id: str
    name: str
    type: str


class RelationshipEdge(BaseModel):
    """Graph relationship edge."""
    source: str
    target: str
    type: str


class GraphData(BaseModel):
    """Complete graph structure."""
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]


class QuestionRequest(BaseModel):
    """Request for question answering."""
    question: str = Field(..., description="The question to answer")


class RAGResponse(BaseModel):
    """Response from RAG query."""
    answer: str
    context: str
    method: str
    metadata: Optional[Dict[str, Any]] = None


class ComparisonResponse(BaseModel):
    """Side-by-side comparison of Plain RAG vs GraphRAG."""
    question: str
    plain_rag: Dict[str, Any]
    graph_rag: Dict[str, Any]
    comparison: Dict[str, str]


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    neo4j_connected: bool
    sqlite_connected: bool
    message: str
