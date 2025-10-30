"""
Neo4j database manager for storing and querying knowledge graphs.
Handles entity and relationship storage, graph traversal, and pattern matching.
"""
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Neo4jManager:
    """Manages connections and operations with Neo4j graph database."""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            user: Database username
            password: Database password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_constraints()
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
    
    def _create_constraints(self):
        """Create uniqueness constraints for entity IDs."""
        with self.driver.session() as session:
            try:
                # Constraint for Entity nodes
                session.run("""
                    CREATE CONSTRAINT entity_id IF NOT EXISTS
                    FOR (e:Entity) REQUIRE e.id IS UNIQUE
                """)
                logger.info("Created Neo4j constraints")
            except Exception as e:
                logger.warning(f"Constraint creation warning: {e}")
    
    def add_entity(self, entity_id: str, entity_type: str, name: str, 
                   properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add or update an entity in the graph.
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type/category of the entity (Person, Organization, etc.)
            name: Display name of the entity
            properties: Additional properties to store
            
        Returns:
            True if successful, False otherwise
        """
        with self.driver.session() as session:
            try:
                props = properties or {}
                props.update({
                    'id': entity_id,
                    'type': entity_type,
                    'name': name
                })
                
                query = """
                    MERGE (e:Entity {id: $entity_id})
                    SET e += $props
                    RETURN e
                """
                session.run(query, entity_id=entity_id, props=props)
                return True
            except Exception as e:
                logger.error(f"Error adding entity: {e}")
                return False
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relation_type: str, properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relationship (WORKS_FOR, LOCATED_IN, etc.)
            properties: Additional properties to store on the relationship
            
        Returns:
            True if successful, False otherwise
        """
        with self.driver.session() as session:
            try:
                props = properties or {}
                
                # Sanitize relation type to valid Cypher identifier
                safe_relation = relation_type.upper().replace(' ', '_').replace('-', '_')
                
                query = f"""
                    MATCH (s:Entity {{id: $source_id}})
                    MATCH (t:Entity {{id: $target_id}})
                    MERGE (s)-[r:{safe_relation}]->(t)
                    SET r += $props
                    RETURN r
                """
                session.run(query, source_id=source_id, target_id=target_id, props=props)
                return True
            except Exception as e:
                logger.error(f"Error adding relationship: {e}")
                return False
    
    def get_entity_neighborhood(self, entity_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Get the neighborhood of an entity up to max_depth hops.
        This is used for GraphRAG context retrieval.
        
        Args:
            entity_id: ID of the entity to start from
            max_depth: Maximum number of hops to traverse
            
        Returns:
            Dictionary containing nodes and relationships in the neighborhood
        """
        with self.driver.session() as session:
            try:
                query = """
                    MATCH path = (start:Entity {id: $entity_id})-[*1..%d]-(connected:Entity)
                    WITH start, connected, relationships(path) as rels
                    RETURN DISTINCT 
                        start,
                        collect(DISTINCT connected) as neighbors,
                        collect(DISTINCT rels) as relationships
                """ % max_depth
                
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if not record:
                    return {"nodes": [], "relationships": []}
                
                nodes = []
                relationships = []
                
                # Add start node
                start_node = record["start"]
                nodes.append(dict(start_node))
                
                # Add connected nodes
                for neighbor in record["neighbors"]:
                    nodes.append(dict(neighbor))
                
                # Add relationships
                for rel_list in record["relationships"]:
                    for rel in rel_list:
                        relationships.append({
                            "type": rel.type,
                            "start": rel.start_node["id"],
                            "end": rel.end_node["id"],
                            "properties": dict(rel)
                        })
                
                return {"nodes": nodes, "relationships": relationships}
                
            except Exception as e:
                logger.error(f"Error getting entity neighborhood: {e}")
                return {"nodes": [], "relationships": []}
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entities by name (fuzzy matching).
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching entities
        """
        with self.driver.session() as session:
            try:
                cypher_query = """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($query)
                    RETURN e
                    LIMIT $limit
                """
                results = session.run(cypher_query, query=query, limit=limit)
                return [dict(record["e"]) for record in results]
            except Exception as e:
                logger.error(f"Error searching entities: {e}")
                return []
    
    def get_all_entities_and_relationships(self) -> Dict[str, Any]:
        """
        Get all entities and relationships in the graph.
        Used for visualization.
        
        Returns:
            Dictionary containing all nodes and relationships
        """
        with self.driver.session() as session:
            try:
                query = """
                    MATCH (n:Entity)
                    OPTIONAL MATCH (n)-[r]->(m:Entity)
                    RETURN collect(DISTINCT n) as nodes, 
                           collect(DISTINCT {
                               type: type(r), 
                               start: n.id, 
                               end: m.id,
                               properties: properties(r)
                           }) as relationships
                """
                result = session.run(query)
                record = result.single()
                
                if not record:
                    return {"nodes": [], "relationships": []}
                
                nodes = [dict(node) for node in record["nodes"]]
                relationships = [rel for rel in record["relationships"] if rel["type"]]
                
                return {"nodes": nodes, "relationships": relationships}
                
            except Exception as e:
                logger.error(f"Error getting all entities and relationships: {e}")
                return {"nodes": [], "relationships": []}
    
    def clear_database(self) -> bool:
        """
        Clear all nodes and relationships from the database.
        Use with caution!
        
        Returns:
            True if successful, False otherwise
        """
        with self.driver.session() as session:
            try:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Database cleared successfully")
                return True
            except Exception as e:
                logger.error(f"Error clearing database: {e}")
                return False
