"""
Graph visualization and query API endpoints.
Provides access to the knowledge graph structure and search.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

from models.schemas import GraphData
from database.neo4j_manager import Neo4jManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/", response_model=GraphData)
async def get_full_graph(neo4j_manager: Neo4jManager = Depends()):
    """
    Get the entire knowledge graph for visualization.
    Returns all entities and their relationships.
    
    Returns:
        Complete graph structure with nodes and edges
    """
    try:
        graph_data = neo4j_manager.get_all_entities_and_relationships()
        return graph_data
    except Exception as e:
        logger.error(f"Error getting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity/{entity_id}")
async def get_entity_neighborhood(
    entity_id: str, 
    max_depth: int = 2,
    neo4j_manager: Neo4jManager = Depends()
):
    """
    Get the neighborhood around a specific entity.
    Useful for focused graph exploration.
    
    Args:
        entity_id: ID of the entity
        max_depth: Maximum traversal depth (default: 2)
        
    Returns:
        Subgraph containing the entity and its neighbors
    """
    try:
        neighborhood = neo4j_manager.get_entity_neighborhood(entity_id, max_depth)
        if not neighborhood['nodes']:
            raise HTTPException(status_code=404, detail="Entity not found")
        return neighborhood
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity neighborhood: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_entities(
    query: str,
    limit: int = 10,
    neo4j_manager: Neo4jManager = Depends()
):
    """
    Search for entities by name.
    
    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)
        
    Returns:
        List of matching entities
    """
    try:
        results = neo4j_manager.search_entities(query, limit)
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/")
async def clear_graph(neo4j_manager: Neo4jManager = Depends()):
    """
    Clear all data from the knowledge graph.
    Use with caution - this is irreversible!
    
    Returns:
        Success message
    """
    try:
        success = neo4j_manager.clear_database()
        if success:
            return {"message": "Graph cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear graph")
    except Exception as e:
        logger.error(f"Error clearing graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
