# GraphRAG Explorer - Architecture Documentation

## System Overview

GraphRAG Explorer is a full-stack application demonstrating the advantages of Graph-based Retrieval-Augmented Generation (GraphRAG) over traditional Plain RAG approaches. The system processes documents, extracts knowledge graphs, and provides intelligent question answering.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                   (React + Tailwind)                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Document   │  │    Graph     │  │     RAG      │  │
│  │    Upload    │  │ Visualization│  │  Comparison  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP REST API
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              API Layer (Routers)                 │   │
│  │  • Documents  • Graph  • RAG  • Health          │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │              Service Layer                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐    │   │
│  │  │Document  │ │   LLM    │ │     RAG      │    │   │
│  │  │Processor │ │ Service  │ │   Service    │    │   │
│  │  └──────────┘ └──────────┘ └──────────────┘    │   │
│  └──────────────────┬───────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼───────────────────────────────┐   │
│  │           Database Layer                         │   │
│  │  ┌──────────────┐     ┌──────────────┐         │   │
│  │  │   SQLite     │     │    Neo4j     │         │   │
│  │  │   Manager    │     │   Manager    │         │   │
│  │  └──────────────┘     └──────────────┘         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────┬───────────────────┬────────────────────────┘
              │                   │
       ┌──────▼──────┐     ┌─────▼─────┐
       │   SQLite    │     │   Neo4j   │
       │  Database   │     │ Database  │
       └─────────────┘     └───────────┘
              │                   │
       ┌──────▼──────┐     ┌─────▼─────┐
       │  Documents  │     │ Knowledge │
       │  Embeddings │     │   Graph   │
       │   Chunks    │     │  Entities │
       └─────────────┘     └───────────┘
```

## Component Details

### Frontend (React)

**Location**: `/frontend/src/`

#### Key Components:

1. **App.jsx** - Main application container
   - Manages global state
   - Health check monitoring
   - Layout and routing

2. **DocumentUpload.jsx** - Document upload interface
   - File selection (text/PDF)
   - Upload progress tracking
   - Success/error feedback
   - Displays extraction statistics

3. **GraphVisualization.jsx** - Interactive graph display
   - Uses vis-network for rendering
   - Color-coded entity types
   - Pan/zoom/hover interactions
   - Auto-refresh on updates

4. **RAGComparison.jsx** - Question answering interface
   - Side-by-side comparison
   - Plain RAG vs GraphRAG results
   - Context visualization
   - Performance insights

#### Services:

- **api.js** - API client for backend communication
  - Axios-based HTTP requests
  - Centralized error handling
  - Request/response transformation

### Backend (FastAPI)

**Location**: `/backend/`

#### API Layer (Routers)

**Location**: `/backend/routers/`

1. **documents.py** - Document management
   - `POST /api/documents/upload` - Upload and process files
   - `GET /api/documents/` - List all documents
   - `GET /api/documents/{id}` - Get specific document
   - `DELETE /api/documents/{id}` - Delete document

2. **graph.py** - Graph operations
   - `GET /api/graph/` - Get full knowledge graph
   - `GET /api/graph/entity/{id}` - Get entity neighborhood
   - `GET /api/graph/search` - Search entities
   - `DELETE /api/graph/` - Clear graph

3. **rag.py** - RAG query endpoints
   - `POST /api/rag/plain` - Plain RAG query
   - `POST /api/rag/graph` - GraphRAG query
   - `POST /api/rag/compare` - Compare both approaches

#### Service Layer

**Location**: `/backend/services/`

1. **document_processor.py** - Document processing
   - PDF text extraction (PyPDF2)
   - Text file reading
   - Intelligent text chunking with overlap
   - Sentence boundary detection

2. **llm_service.py** - LLM operations
   - Entity/relationship extraction
   - Vector embedding generation
   - Question answering with context
   - Batch processing for efficiency

3. **rag_service.py** - RAG implementation
   - **Plain RAG**: Vector similarity search
     - Cosine similarity calculation
     - Top-k chunk retrieval
     - Context assembly
   - **GraphRAG**: Graph traversal
     - Entity identification from query
     - Neighborhood retrieval
     - Structured context building
   - Comparison and analysis

#### Database Layer

**Location**: `/backend/database/`

1. **neo4j_manager.py** - Neo4j operations
   - Entity CRUD operations
   - Relationship management
   - Graph traversal (Cypher queries)
   - Neighborhood retrieval
   - Pattern matching and search

2. **sqlite_manager.py** - SQLite operations
   - Document storage
   - Text chunk management
   - Vector embedding storage (pickled)
   - Metadata tracking

### Data Flow

#### Document Upload Flow

```
1. User uploads file (Frontend)
   ↓
2. File sent to backend API
   ↓
3. DocumentProcessor extracts text
   ↓
4. Text split into chunks
   ↓
5. LLMService generates embeddings
   ↓
6. Chunks + embeddings → SQLite
   ↓
7. LLMService extracts entities/relationships
   ↓
8. Entities → Neo4j nodes
   ↓
9. Relationships → Neo4j edges
   ↓
10. Success response to Frontend
```

#### Plain RAG Query Flow

```
1. User asks question (Frontend)
   ↓
2. Question sent to /api/rag/plain
   ↓
3. LLMService generates question embedding
   ↓
4. RAGService finds similar chunks (cosine similarity)
   ↓
5. Top-k chunks retrieved from SQLite
   ↓
6. Context assembled from chunks
   ↓
7. LLMService generates answer with context
   ↓
8. Answer + metadata returned to Frontend
```

#### GraphRAG Query Flow

```
1. User asks question (Frontend)
   ↓
2. Question sent to /api/rag/graph
   ↓
3. RAGService extracts entities from question
   ↓
4. Neo4jManager searches for matching entities
   ↓
5. Graph neighborhood retrieved (Cypher traversal)
   ↓
6. Structured context built from graph
   ↓
7. LLMService generates answer with graph context
   ↓
8. Answer + graph metadata returned to Frontend
```

## Database Schemas

### Neo4j Graph Schema

```cypher
// Node: Entity
(:Entity {
    id: String,           // Unique identifier
    name: String,         // Display name
    type: String          // Entity type (Person, Organization, etc.)
})

// Relationship: Dynamic types
(source:Entity)-[r:RELATIONSHIP_TYPE]->(target:Entity)
// Examples: WORKS_FOR, LOCATED_IN, FOUNDED_BY, etc.
```

### SQLite Schema

```sql
-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL
);

-- Text chunks with embeddings
CREATE TABLE text_chunks (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding BLOB,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

## Key Design Decisions

### 1. Dual Storage Strategy

**Why**: Different RAG approaches need different data structures
- SQLite for vector similarity (Plain RAG)
- Neo4j for graph traversal (GraphRAG)

### 2. Chunk Overlap

**Why**: Maintains context across boundaries
- 50-character overlap between chunks
- Prevents loss of information at split points

### 3. Entity Extraction via LLM

**Why**: Flexible and accurate
- Can handle any document type
- Adapts to domain-specific entities
- No need for pre-trained NER models

### 4. Graph Traversal with Cypher

**Why**: Native and efficient
- Neo4j's query language
- Optimized for pattern matching
- Supports complex traversals

### 5. Side-by-Side Comparison

**Why**: Educational value
- Shows clear differences
- Demonstrates GraphRAG advantages
- Helps understand trade-offs

## Scalability Considerations

### Current Limitations

1. **Single-threaded processing**: Documents processed sequentially
2. **In-memory graph loading**: Full graph loaded for visualization
3. **No caching**: LLM calls not cached
4. **Local deployment**: Single-machine setup

### Potential Improvements

1. **Async processing**: Use Celery for background tasks
2. **Streaming**: Process large documents in streams
3. **Caching**: Redis for LLM response caching
4. **Pagination**: API pagination for large result sets
5. **Distributed**: Kubernetes deployment for scaling

## Security Considerations

1. **API Key Protection**: Never commit API keys
2. **Input Validation**: File type and size limits
3. **SQL Injection**: Parameterized queries
4. **Cypher Injection**: Parameterized Cypher queries
5. **CORS**: Configured for specific origins

## Performance Optimizations

1. **Batch Processing**: Multiple chunks processed together
2. **Connection Pooling**: Database connection reuse
3. **Index Creation**: Neo4j constraints for fast lookups
4. **Vector Storage**: Efficient binary serialization
5. **Frontend Lazy Loading**: Components loaded on demand

## Testing Strategy

### Unit Tests (Recommended)

- Service layer functions
- Database operations
- API endpoints
- Frontend components

### Integration Tests (Recommended)

- End-to-end document upload
- RAG query flow
- Graph operations

### Manual Testing

- UI/UX validation
- Browser compatibility
- Performance testing

## Deployment Options

### 1. Docker Compose (Development)

- Easy local setup
- All services in containers
- Suitable for demos

### 2. Kubernetes (Production)

- Scalable deployment
- High availability
- Load balancing
- Auto-scaling

### 3. Cloud Services

- AWS: ECS + RDS + DocumentDB
- GCP: Cloud Run + Cloud SQL + Firestore
- Azure: Container Instances + Cosmos DB

## Monitoring and Logging

### Current Implementation

- Python logging module
- Console output
- No persistent logs

### Production Recommendations

1. **Structured Logging**: JSON format
2. **Log Aggregation**: ELK stack or CloudWatch
3. **Metrics**: Prometheus + Grafana
4. **Tracing**: OpenTelemetry
5. **Error Tracking**: Sentry

## Future Enhancements

1. **Multi-modal Support**: Images, audio, video
2. **Collaborative Editing**: Real-time graph updates
3. **Advanced Visualization**: 3D graphs, filtering
4. **Custom Entity Types**: User-defined schemas
5. **Export Functionality**: Graph export to various formats
6. **Authentication**: User accounts and permissions
7. **API Rate Limiting**: Prevent abuse
8. **Batch Upload**: Multiple documents at once
9. **Query History**: Save and review past queries
10. **Model Selection**: Choose different LLMs

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [React Documentation](https://react.dev/)
- [Vis.js Network Documentation](https://visjs.github.io/vis-network/docs/network/)
