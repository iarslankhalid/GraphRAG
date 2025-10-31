"""
RAG service comparing Plain RAG (vector similarity) vs GraphRAG (graph traversal).
Demonstrates how graph context improves reasoning and answer quality.
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Implements both plain RAG and GraphRAG approaches for comparison.
    """
    
    def __init__(self, sqlite_manager, neo4j_manager, llm_service):
        """
        Initialize RAG service with database managers and LLM service.
        
        Args:
            sqlite_manager: SQLiteManager instance for vector search
            neo4j_manager: Neo4jManager instance for graph traversal
            llm_service: LLMService instance for embeddings and generation
        """
        self.sqlite_manager = sqlite_manager
        self.neo4j_manager = neo4j_manager
        self.llm_service = llm_service
    
    def _find_similar_chunks(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find text chunks most similar to query using vector similarity.
        This is the retrieval step for plain RAG.
        
        Args:
            query_embedding: Vector embedding of the query
            top_k: Number of top results to return
            
        Returns:
            List of most similar chunks with similarity scores
        """
        # Get all chunks with embeddings
        chunks = self.sqlite_manager.get_all_chunks_with_embeddings()
        
        if not chunks:
            logger.warning("No chunks with embeddings found")
            return []
        
        # Calculate cosine similarity between query and all chunks
        query_vec = np.array(query_embedding).reshape(1, -1)
        similarities = []
        
        for chunk in chunks:
            if chunk['embedding']:
                chunk_vec = np.array(chunk['embedding']).reshape(1, -1)
                similarity = cosine_similarity(query_vec, chunk_vec)[0][0]
                similarities.append({
                    'chunk': chunk,
                    'similarity': float(similarity)
                })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def _extract_entities_from_query(self, query: str) -> List[str]:
        """
        Extract potential entity names from the query.
        This helps identify which graph nodes are relevant.
        
        Args:
            query: User's question
            
        Returns:
            List of potential entity names
        """
        # Simple approach: extract capitalized words and phrases
        # In production, could use NER or LLM for better extraction
        words = query.split()
        entities = []
        
        # Look for capitalized words (potential entity names)
        for i, word in enumerate(words):
            # Skip first word if it's capitalized (likely start of sentence)
            if i > 0 and word[0].isupper() and len(word) > 1:
                entities.append(word)
        
        # Also do a fuzzy search in the graph
        for word in words:
            if len(word) > 3:  # Skip short words
                search_results = self.neo4j_manager.search_entities(word, limit=3)
                for result in search_results:
                    entities.append(result['id'])
        
        return list(set(entities))  # Remove duplicates
    
    def plain_rag_query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Answer question using Plain RAG approach.
        Steps:
        1. Generate embedding for question
        2. Find most similar text chunks using vector similarity
        3. Use LLM to generate answer from retrieved chunks
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary containing answer, context, and metadata
        """
        logger.info(f"Plain RAG query: {question}")
        
        # Generate query embedding
        query_embedding = self.llm_service.generate_embedding(question)
        
        if not query_embedding:
            return {
                "answer": "Error: Could not generate query embedding",
                "context": "",
                "chunks_used": []
            }
        
        # Find similar chunks
        similar_chunks = self._find_similar_chunks(query_embedding, top_k)
        
        if not similar_chunks:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "context": "",
                "chunks_used": []
            }
        
        # Build context from retrieved chunks
        context_parts = []
        chunks_used = []
        
        for item in similar_chunks:
            chunk = item['chunk']
            similarity = item['similarity']
            context_parts.append(f"[Similarity: {similarity:.3f}]\n{chunk['chunk_text']}")
            chunks_used.append({
                'text': chunk['chunk_text'][:100] + '...',
                'similarity': similarity
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using LLM
        answer = self.llm_service.answer_question_with_context(question, context, mode="plain")
        
        return {
            "answer": answer,
            "context": context,
            "chunks_used": chunks_used,
            "method": "Plain RAG (Vector Similarity)"
        }
    
    def graph_rag_query(self, question: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Answer question using GraphRAG approach.
        Steps:
        1. Extract entities from question
        2. Retrieve graph neighborhood around those entities
        3. Build structured context from graph
        4. Use LLM to generate answer with graph context
        
        Args:
            question: User's question
            max_depth: Maximum graph traversal depth
            
        Returns:
            Dictionary containing answer, context, and metadata
        """
        logger.info(f"GraphRAG query: {question}")
        
        # Extract entities from query
        entity_ids = self._extract_entities_from_query(question)
        
        if not entity_ids:
            # Fallback: try to get entire graph if small
            graph_data = self.neo4j_manager.get_all_entities_and_relationships()
            nodes = graph_data.get('nodes', [])
            relationships = graph_data.get('relationships', [])
        else:
            # Get neighborhoods for identified entities
            nodes = []
            relationships = []
            seen_node_ids = set()
            
            for entity_id in entity_ids:
                neighborhood = self.neo4j_manager.get_entity_neighborhood(entity_id, max_depth)
                
                for node in neighborhood.get('nodes', []):
                    if node['id'] not in seen_node_ids:
                        nodes.append(node)
                        seen_node_ids.add(node['id'])
                
                relationships.extend(neighborhood.get('relationships', []))
        
        if not nodes:
            return {
                "answer": "No relevant entities found in the knowledge graph.",
                "context": "",
                "entities_used": [],
                "relationships_used": []
            }
        
        # Build structured context from graph
        context_parts = ["Entities in the knowledge graph:"]
        for node in nodes:
            context_parts.append(f"- {node['name']} ({node['type']})")
        
        context_parts.append("\nRelationships:")
        for rel in relationships:
            # Find node names for better readability
            source_name = next((n['name'] for n in nodes if n['id'] == rel['start']), rel['start'])
            target_name = next((n['name'] for n in nodes if n['id'] == rel['end']), rel['end'])
            context_parts.append(f"- {source_name} --[{rel['type']}]--> {target_name}")
        
        context = "\n".join(context_parts)
        
        # Generate answer using LLM with graph context
        answer = self.llm_service.answer_question_with_context(question, context, mode="graph")
        
        return {
            "answer": answer,
            "context": context,
            "entities_used": [{"name": n['name'], "type": n['type']} for n in nodes],
            "relationships_used": [{"type": r['type']} for r in relationships],
            "method": "GraphRAG (Graph Traversal)"
        }
    
    def compare_rag_approaches(self, question: str) -> Dict[str, Any]:
        """
        Compare Plain RAG vs GraphRAG side-by-side.
        This is the main feature demonstrating the difference in approaches.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing results from both approaches
        """
        logger.info(f"Comparing RAG approaches for: {question}")
        
        plain_result = self.plain_rag_query(question)
        graph_result = self.graph_rag_query(question)
        
        return {
            "question": question,
            "plain_rag": plain_result,
            "graph_rag": graph_result,
            "comparison": {
                "plain_uses": "Vector similarity search over text chunks",
                "graph_uses": "Graph traversal to find connected entities and relationships",
                "key_difference": "GraphRAG preserves structural context and relationships between entities"
            }
        }
