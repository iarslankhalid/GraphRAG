# GraphRAG Explorer - Frequently Asked Questions

## General Questions

### What is GraphRAG?

GraphRAG (Graph-based Retrieval-Augmented Generation) is an approach to question answering that uses knowledge graphs to provide richer context compared to traditional RAG methods. Instead of just finding similar text chunks, GraphRAG understands entities and their relationships, leading to better reasoning and more accurate answers.

### Why is GraphRAG better than Plain RAG?

**Plain RAG** uses vector similarity to find relevant text chunks, which is good for keyword matching but:
- Misses relationships between entities
- Lacks structural understanding
- Cannot reason about connections
- Limited to surface-level matches

**GraphRAG** uses graph traversal to:
- Understand entity relationships
- Provide structural context
- Enable multi-hop reasoning
- Surface hidden connections

### Is this production-ready?

This is a **demo application** designed to showcase the concepts. For production use, you would want to add:
- Authentication and authorization
- Rate limiting
- Better error handling
- Monitoring and logging
- Scalability improvements
- Comprehensive testing

## Technical Questions

### What LLM models are supported?

Currently, the application uses OpenAI's models:
- **GPT-3.5-turbo** for entity extraction and question answering (configurable to GPT-4)
- **text-embedding-ada-002** for vector embeddings

You can modify `backend/config.py` to use different models.

### Can I use a different LLM provider?

Yes! You can modify `backend/services/llm_service.py` to use:
- Anthropic Claude
- Google PaLM
- Hugging Face models
- Local models (LLaMA, Mistral, etc.)

The main changes needed are in the API calls and authentication.

### How much does it cost to run?

**OpenAI API costs** (approximate):
- Document processing: $0.05-0.10 per 1000 words
- Each question: $0.01-0.02
- Embeddings: $0.0001 per 1000 tokens

**Infrastructure**:
- Local Docker: Free
- Cloud hosting: Varies by provider

### What file formats are supported?

Currently:
- **.txt** (plain text files)
- **.pdf** (PDF documents)

Future enhancements could include:
- .docx (Word documents)
- .html (Web pages)
- .md (Markdown files)
- .csv (Structured data)

### How big can documents be?

Default limit: **10MB per file**

This can be changed in `backend/config.py`:
```python
MAX_UPLOAD_SIZE = 10485760  # bytes
```

Note: Larger documents take longer to process and cost more in API calls.

### How accurate is entity extraction?

Accuracy depends on:
- **Document quality**: Clear, well-structured text works best
- **LLM model**: GPT-4 is more accurate than GPT-3.5
- **Domain**: Common topics work better than highly specialized content

Typical accuracy: 85-95% for well-written documents.

### Can I customize entity types?

Yes! Modify the prompt in `backend/services/llm_service.py`:
```python
prompt = f"""Extract entities and relationships from the following text.
For each entity, provide:
- type: entity type (Person, Organization, [ADD YOUR TYPES HERE])
"""
```

### How does graph visualization work?

We use **vis-network** library which:
- Renders nodes (entities) and edges (relationships)
- Provides interactive pan/zoom
- Colors nodes by entity type
- Shows tooltips on hover
- Uses force-directed layout algorithm

### Can I export the knowledge graph?

Currently, no built-in export. But you can:
1. Access Neo4j Browser at http://localhost:7474
2. Use Cypher queries to export data
3. Add export functionality to the API

Example Cypher export:
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
```

## Usage Questions

### Why is processing slow?

Several factors affect speed:
1. **LLM API calls**: Each chunk needs processing
2. **Document size**: Larger docs = more chunks
3. **Network latency**: API call round-trips
4. **Rate limits**: OpenAI has per-minute limits

Typical processing time: 30 seconds to 2 minutes per document.

### Can I process multiple documents?

Yes! Upload documents one at a time. All entities and relationships are combined into a single knowledge graph.

### What happens if extraction fails?

The system is designed to be resilient:
- Failed chunks are logged but don't stop processing
- Partial results are still saved
- You can re-upload the document
- Check backend logs for error details

### How do I improve answer quality?

1. **Better documents**: Clear, well-structured text
2. **More context**: Upload related documents
3. **Better questions**: Specific, focused queries
4. **Model upgrade**: Use GPT-4 instead of GPT-3.5
5. **Graph refinement**: Manually correct entities in Neo4j

### Can I edit the knowledge graph?

Yes! Use Neo4j Browser:
1. Go to http://localhost:7474
2. Login (neo4j/password)
3. Use Cypher queries to add/edit/delete

Example - Add entity:
```cypher
CREATE (e:Entity {id: 'new_entity', name: 'New Entity', type: 'Custom'})
```

Example - Add relationship:
```cypher
MATCH (a:Entity {id: 'entity1'}), (b:Entity {id: 'entity2'})
CREATE (a)-[:CUSTOM_RELATION]->(b)
```

### Why are Plain RAG and GraphRAG giving similar answers?

This can happen when:
1. **Simple questions**: No relationships needed
2. **Small graph**: Not enough entities to showcase advantages
3. **Well-matched chunks**: Plain RAG finds perfect text
4. **Question phrasing**: Doesn't mention entities

Try questions that require understanding relationships:
- "What is the relationship between X and Y?"
- "How are A, B, and C connected?"
- "Who does X work with?"

## Setup Questions

### Do I need a GPU?

No! The application runs on CPU. LLM processing is done via API calls to OpenAI's servers.

### Can I run this offline?

Not by default, since it uses OpenAI's API. But you could:
1. Use local LLM models (LLaMA, Mistral)
2. Use local embedding models (sentence-transformers)
3. Modify the code to support offline mode

### What are the system requirements?

**Minimum**:
- 4GB RAM
- 2 CPU cores
- 10GB disk space
- Docker installed

**Recommended**:
- 8GB RAM
- 4 CPU cores
- 20GB disk space
- Fast internet connection

### Can I deploy to cloud?

Yes! The application can be deployed to:
- **AWS**: ECS, Fargate, or EKS
- **Google Cloud**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **DigitalOcean**: App Platform or Kubernetes
- **Heroku**: Container deployment

See `ARCHITECTURE.md` for deployment options.

### How do I backup my data?

**Neo4j**:
```bash
docker exec graphrag-neo4j neo4j-admin dump --to=/backups/neo4j.dump
```

**SQLite**:
```bash
cp data/graphrag.db data/graphrag.db.backup
```

**Full backup**:
```bash
docker-compose down
tar -czf graphrag-backup.tar.gz data/
```

## Troubleshooting

### "Cannot connect to backend"

1. Check if backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify URL in `frontend/.env`: `VITE_API_URL=http://localhost:8000`
4. Try accessing API directly: http://localhost:8000/api/health

### "Neo4j connection failed"

1. Check if Neo4j is running: `docker-compose ps neo4j`
2. Wait 30 seconds for Neo4j to start
3. Check Neo4j logs: `docker-compose logs neo4j`
4. Verify credentials in `backend/.env`
5. Try accessing Neo4j Browser: http://localhost:7474

### "Invalid OpenAI API key"

1. Verify key is correct in `backend/.env`
2. Check key has credits at https://platform.openai.com/
3. Ensure no extra spaces or quotes around key
4. Try generating a new key

### "Graph visualization is empty"

1. Upload a document first
2. Wait for processing to complete
3. Click the Refresh button
4. Check Neo4j Browser for data
5. View backend logs for errors

### "Port already in use"

Another service is using the port. Solutions:
1. Stop conflicting service
2. Change port in `docker-compose.yml`
3. Use different port numbers

### "Out of memory"

1. Increase Docker memory limit
2. Process smaller documents
3. Reduce chunk size in `document_processor.py`

## Best Practices

### Document Upload

1. **Clean text**: Remove formatting, headers, footers
2. **Structured content**: Well-organized documents work better
3. **Reasonable size**: 1000-5000 words is optimal
4. **Domain-specific**: Upload related documents together

### Asking Questions

1. **Be specific**: "Who is the CEO?" vs "Tell me about leadership"
2. **Use entity names**: Mention specific people, places, things
3. **Ask about relationships**: "How is X related to Y?"
4. **One question at a time**: Focus on single aspect

### Graph Building

1. **Consistent naming**: Use full names consistently
2. **Related documents**: Upload documents from same domain
3. **Incremental growth**: Add documents gradually
4. **Verification**: Check graph in Neo4j Browser

### Performance

1. **Batch uploads**: Process multiple small documents
2. **Off-peak usage**: Avoid OpenAI rate limits
3. **Monitor costs**: Track API usage
4. **Cache results**: Save common queries

## Advanced Topics

### Can I train my own models?

Yes, you could:
1. Fine-tune GPT models for your domain
2. Train custom entity extraction models
3. Create domain-specific embeddings
4. Build custom relationship extractors

### Can I use this for commercial applications?

The code is open source (check LICENSE). However:
- OpenAI API has terms of service
- Neo4j has licensing considerations
- Consider data privacy and security
- Add proper authentication and authorization

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Where can I learn more about GraphRAG?

Resources:
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/)
- [Neo4j GraphRAG examples](https://neo4j.com/developer/genai/)
- [LangChain documentation](https://python.langchain.com/)
- [RAG survey papers](https://arxiv.org/abs/2312.10997)

### Can I integrate this with my existing application?

Yes! The FastAPI backend can be:
- Used as a standalone API service
- Integrated via REST API calls
- Embedded in larger applications
- Extended with custom endpoints

### What's the roadmap for future features?

Planned enhancements:
- Multi-modal support (images, audio)
- Real-time collaboration
- Custom entity types
- Advanced visualizations
- Export functionality
- User authentication
- API rate limiting
- Batch processing

---

## Still have questions?

- Open an issue on GitHub
- Check the documentation in `README.md`, `SETUP.md`, and `ARCHITECTURE.md`
- Review the code - it's well-commented!
