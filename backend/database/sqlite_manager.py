"""
SQLite database manager for storing document metadata and text embeddings.
Used for plain RAG (vector similarity search) comparison with GraphRAG.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import pickle
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Document(Base):
    """Store uploaded document metadata."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_type = Column(String, nullable=False)  # 'text' or 'pdf'


class TextChunk(Base):
    """Store document chunks with embeddings for vector search."""
    __tablename__ = 'text_chunks'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    # Store embedding as pickled numpy array for efficient storage
    embedding = Column(LargeBinary, nullable=True)


class SQLiteManager:
    """Manages SQLite database operations for document storage and embeddings."""
    
    def __init__(self, db_path: str):
        """
        Initialize SQLite connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"SQLite database initialized at {db_path}")
    
    def add_document(self, filename: str, content: str, file_type: str) -> int:
        """
        Add a new document to the database.
        
        Args:
            filename: Name of the uploaded file
            content: Full text content of the document
            file_type: Type of file ('text' or 'pdf')
            
        Returns:
            Document ID
        """
        try:
            doc = Document(
                filename=filename,
                content=content,
                file_type=file_type
            )
            self.session.add(doc)
            self.session.commit()
            logger.info(f"Added document: {filename} with ID: {doc.id}")
            return doc.id
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding document: {e}")
            raise
    
    def add_text_chunk(self, document_id: int, chunk_text: str, 
                       chunk_index: int, embedding: Optional[List[float]] = None) -> int:
        """
        Add a text chunk with optional embedding.
        
        Args:
            document_id: ID of parent document
            chunk_text: Text content of the chunk
            chunk_index: Index of this chunk in the document
            embedding: Vector embedding of the chunk
            
        Returns:
            Chunk ID
        """
        try:
            # Serialize embedding as pickle for efficient storage
            embedding_blob = pickle.dumps(embedding) if embedding else None
            
            chunk = TextChunk(
                document_id=document_id,
                chunk_text=chunk_text,
                chunk_index=chunk_index,
                embedding=embedding_blob
            )
            self.session.add(chunk)
            self.session.commit()
            return chunk.id
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding text chunk: {e}")
            raise
    
    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by ID.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document data as dictionary or None if not found
        """
        doc = self.session.query(Document).filter_by(id=document_id).first()
        if doc:
            return {
                'id': doc.id,
                'filename': doc.filename,
                'content': doc.content,
                'upload_date': doc.upload_date.isoformat(),
                'file_type': doc.file_type
            }
        return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents in the database.
        
        Returns:
            List of document dictionaries
        """
        docs = self.session.query(Document).all()
        return [{
            'id': doc.id,
            'filename': doc.filename,
            'content': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content,
            'upload_date': doc.upload_date.isoformat(),
            'file_type': doc.file_type
        } for doc in docs]
    
    def get_chunks_by_document(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List of chunk dictionaries
        """
        chunks = self.session.query(TextChunk).filter_by(document_id=document_id).all()
        result = []
        for chunk in chunks:
            embedding = pickle.loads(chunk.embedding) if chunk.embedding else None
            result.append({
                'id': chunk.id,
                'document_id': chunk.document_id,
                'chunk_text': chunk.chunk_text,
                'chunk_index': chunk.chunk_index,
                'embedding': embedding
            })
        return result
    
    def get_all_chunks_with_embeddings(self) -> List[Dict[str, Any]]:
        """
        Get all chunks that have embeddings.
        Used for vector similarity search in plain RAG.
        
        Returns:
            List of chunk dictionaries with embeddings
        """
        chunks = self.session.query(TextChunk).filter(TextChunk.embedding.isnot(None)).all()
        result = []
        for chunk in chunks:
            embedding = pickle.loads(chunk.embedding) if chunk.embedding else None
            result.append({
                'id': chunk.id,
                'document_id': chunk.document_id,
                'chunk_text': chunk.chunk_text,
                'chunk_index': chunk.chunk_index,
                'embedding': embedding
            })
        return result
    
    def delete_document(self, document_id: int) -> bool:
        """
        Delete a document and all its chunks.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete chunks first
            self.session.query(TextChunk).filter_by(document_id=document_id).delete()
            # Delete document
            self.session.query(Document).filter_by(id=document_id).delete()
            self.session.commit()
            logger.info(f"Deleted document {document_id} and its chunks")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting document: {e}")
            return False
    
    def close(self):
        """Close the database session."""
        self.session.close()
