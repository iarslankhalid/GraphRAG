"""
Document management API endpoints.
Handles upload, processing, and storage of text/PDF documents.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import shutil
import logging

from models.schemas import DocumentUploadResponse, DocumentInfo
from services.document_processor import DocumentProcessor
from services.llm_service import LLMService
from database.sqlite_manager import SQLiteManager
from database.neo4j_manager import Neo4jManager
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Initialize services (will be replaced with dependency injection in main app)
document_processor = DocumentProcessor()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    sqlite_manager: SQLiteManager = Depends(),
    neo4j_manager: Neo4jManager = Depends(),
    llm_service: LLMService = Depends()
):
    """
    Upload and process a document (text or PDF).
    
    Steps:
    1. Save uploaded file
    2. Extract text content
    3. Split into chunks
    4. Generate embeddings for chunks
    5. Extract entities and relationships using LLM
    6. Store in Neo4j (graph) and SQLite (vectors)
    
    Args:
        file: Uploaded file (text or PDF)
        
    Returns:
        Processing results including entities and relationships extracted
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext == '.pdf':
        file_type = 'pdf'
    elif file_ext in ['.txt', '.text']:
        file_type = 'text'
    else:
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(settings.upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process document
        full_text, chunks = document_processor.process_file(file_path, file_type)
        
        # Store document in SQLite
        doc_id = sqlite_manager.add_document(file.filename, full_text, file_type)
        
        # Generate embeddings and store chunks
        for i, chunk in enumerate(chunks):
            embedding = llm_service.generate_embedding(chunk)
            sqlite_manager.add_text_chunk(doc_id, chunk, i, embedding)
        
        # Extract entities and relationships using LLM
        entities, relationships = llm_service.batch_extract_from_chunks(chunks)
        
        # Store in Neo4j
        for entity in entities:
            neo4j_manager.add_entity(
                entity_id=entity['id'],
                entity_type=entity['type'],
                name=entity['name']
            )
        
        for rel in relationships:
            neo4j_manager.add_relationship(
                source_id=rel['source'],
                target_id=rel['target'],
                relation_type=rel['type']
            )
        
        logger.info(f"Successfully processed document: {file.filename}")
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            entities_extracted=len(entities),
            relationships_extracted=len(relationships),
            chunks_created=len(chunks),
            message="Document processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/", response_model=List[DocumentInfo])
async def list_documents(sqlite_manager: SQLiteManager = Depends()):
    """
    Get list of all uploaded documents.
    
    Returns:
        List of document metadata
    """
    try:
        documents = sqlite_manager.get_all_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(document_id: int, sqlite_manager: SQLiteManager = Depends()):
    """
    Get details of a specific document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        Document metadata and content
    """
    try:
        document = sqlite_manager.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: int, sqlite_manager: SQLiteManager = Depends()):
    """
    Delete a document and its associated data.
    
    Args:
        document_id: ID of the document to delete
        
    Returns:
        Success message
    """
    try:
        success = sqlite_manager.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
