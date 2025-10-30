"""
Document processing service for handling text and PDF files.
Extracts text content and splits into chunks for processing.
"""
from PyPDF2 import PdfReader
from typing import List, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents and splits them into manageable chunks."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """
        Read text content from a text file.
        
        Args:
            txt_path: Path to the text file
            
        Returns:
            File content as string
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Read {len(text)} characters from text file")
            return text
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for processing.
        This helps maintain context across chunk boundaries.
        
        Args:
            text: Full text to split
            
        Returns:
            List of text chunks
        """
        # Clean up text: normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence boundary
            if end < text_length:
                # Look for sentence ending punctuation
                for punct in ['. ', '! ', '? ', '\n']:
                    punct_pos = text.rfind(punct, start, end)
                    if punct_pos != -1:
                        end = punct_pos + 1
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else text_length
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def process_file(self, file_path: str, file_type: str) -> Tuple[str, List[str]]:
        """
        Process a file and return full text and chunks.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('text' or 'pdf')
            
        Returns:
            Tuple of (full_text, list_of_chunks)
        """
        # Extract text based on file type
        if file_type == 'pdf':
            full_text = self.extract_text_from_pdf(file_path)
        elif file_type == 'text':
            full_text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Split into chunks
        chunks = self.split_text_into_chunks(full_text)
        
        return full_text, chunks
