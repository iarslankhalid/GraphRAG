"""
RAG query API endpoints.
Provides both Plain RAG and GraphRAG question answering with side-by-side comparison.
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from models.schemas import QuestionRequest, RAGResponse, ComparisonResponse
from services.rag_service import RAGService
from services.llm_service import LLMService
from database.sqlite_manager import SQLiteManager
from database.neo4j_manager import Neo4jManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/plain", response_model=RAGResponse)
async def plain_rag_query(
    request: QuestionRequest,
    sqlite_manager: SQLiteManager = Depends(),
    neo4j_manager: Neo4jManager = Depends(),
    llm_service: LLMService = Depends()
):
    """
    Answer a question using Plain RAG (vector similarity search).
    
    This approach:
    1. Embeds the question as a vector
    2. Finds similar text chunks using cosine similarity
    3. Generates answer from retrieved chunks
    
    Args:
        request: Question to answer
        
    Returns:
        Answer with context and metadata
    """
    try:
        rag_service = RAGService(sqlite_manager, neo4j_manager, llm_service)
        result = rag_service.plain_rag_query(request.question)
        
        return RAGResponse(
            answer=result['answer'],
            context=result['context'],
            method=result['method'],
            metadata={"chunks_used": result.get('chunks_used', [])}
        )
    except Exception as e:
        logger.error(f"Error in plain RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph", response_model=RAGResponse)
async def graph_rag_query(
    request: QuestionRequest,
    sqlite_manager: SQLiteManager = Depends(),
    neo4j_manager: Neo4jManager = Depends(),
    llm_service: LLMService = Depends()
):
    """
    Answer a question using GraphRAG (graph traversal).
    
    This approach:
    1. Extracts entities from the question
    2. Retrieves graph neighborhood around those entities
    3. Generates answer using structured graph context
    
    Args:
        request: Question to answer
        
    Returns:
        Answer with graph context and metadata
    """
    try:
        rag_service = RAGService(sqlite_manager, neo4j_manager, llm_service)
        result = rag_service.graph_rag_query(request.question)
        
        return RAGResponse(
            answer=result['answer'],
            context=result['context'],
            method=result['method'],
            metadata={
                "entities_used": result.get('entities_used', []),
                "relationships_used": result.get('relationships_used', [])
            }
        )
    except Exception as e:
        logger.error(f"Error in graph RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_rag_approaches(
    request: QuestionRequest,
    sqlite_manager: SQLiteManager = Depends(),
    neo4j_manager: Neo4jManager = Depends(),
    llm_service: LLMService = Depends()
):
    """
    Compare Plain RAG vs GraphRAG side-by-side.
    
    This is the main feature demonstrating how graph context
    improves reasoning compared to simple vector similarity.
    
    Args:
        request: Question to answer
        
    Returns:
        Results from both approaches with comparison insights
    """
    try:
        rag_service = RAGService(sqlite_manager, neo4j_manager, llm_service)
        result = rag_service.compare_rag_approaches(request.question)
        return result
    except Exception as e:
        logger.error(f"Error in RAG comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))
