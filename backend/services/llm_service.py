"""
LLM service for entity/relationship extraction and text generation.
Uses OpenAI GPT models for knowledge graph construction and question answering.
"""
import openai
from typing import List, Dict, Any, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Handles all LLM-based operations including extraction and generation."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", embedding_model: str = "text-embedding-ada-002"):
        """
        Initialize LLM service.
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use for text generation
            embedding_model: Model to use for embeddings
        """
        openai.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        logger.info(f"Initialized LLM service with model: {model}")
    
    def extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """
        Extract entities and relationships from text using LLM.
        This is the core of building the knowledge graph.
        
        Args:
            text: Text to extract from
            
        Returns:
            Dictionary containing entities and relationships
        """
        try:
            # Construct prompt for entity/relationship extraction
            prompt = f"""Extract entities and relationships from the following text.
Return your response as a JSON object with two arrays: "entities" and "relationships".

For each entity, provide:
- id: a unique lowercase identifier (e.g., "john_doe")
- name: the display name
- type: entity type (Person, Organization, Location, Concept, etc.)

For each relationship, provide:
- source: id of source entity
- target: id of target entity
- type: relationship type (WORKS_FOR, LOCATED_IN, RELATES_TO, etc.)

Text:
{text}

JSON:"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from text. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            
            # Sometimes LLM wraps JSON in code blocks, clean that up
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            
            logger.info(f"Extracted {len(result.get('entities', []))} entities and {len(result.get('relationships', []))} relationships")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {"entities": [], "relationships": []}
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {"entities": [], "relationships": []}
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.
        Used for plain RAG vector similarity search.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response['data'][0]['embedding']
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def answer_question_with_context(self, question: str, context: str, mode: str = "plain") -> str:
        """
        Answer a question using provided context.
        
        Args:
            question: User's question
            context: Relevant context to use for answering
            mode: "plain" for plain RAG or "graph" for GraphRAG
            
        Returns:
            Generated answer
        """
        try:
            # Customize prompt based on mode
            if mode == "graph":
                system_prompt = """You are a helpful assistant that answers questions using knowledge from a graph database.
The context provided includes entities and their relationships. Use this structured information to provide accurate, detailed answers.
Explain how the relationships between entities help answer the question."""
            else:
                system_prompt = """You are a helpful assistant that answers questions based on provided text.
Use only the information in the context to answer the question. Be concise and accurate."""
            
            prompt = f"""Context:
{context}

Question: {question}

Answer:"""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer using {mode} RAG")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def batch_extract_from_chunks(self, chunks: List[str]) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract entities and relationships from multiple text chunks.
        Aggregates results from all chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Tuple of (all_entities, all_relationships)
        """
        all_entities = []
        all_relationships = []
        entity_ids_seen = set()
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            result = self.extract_entities_and_relations(chunk)
            
            # Add entities (deduplicate by id)
            for entity in result.get('entities', []):
                if entity['id'] not in entity_ids_seen:
                    all_entities.append(entity)
                    entity_ids_seen.add(entity['id'])
            
            # Add relationships
            all_relationships.extend(result.get('relationships', []))
        
        logger.info(f"Total: {len(all_entities)} unique entities, {len(all_relationships)} relationships")
        return all_entities, all_relationships
