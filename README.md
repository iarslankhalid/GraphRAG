# GraphRAG Explorer

A full-stack demo application showcasing the difference between **Plain RAG** (Retrieval-Augmented Generation) and **GraphRAG** for intelligent question answering. This application demonstrates how knowledge graphs can significantly improve reasoning and answer quality compared to traditional vector similarity search.

![GraphRAG Explorer](https://img.shields.io/badge/Status-Demo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-blue)
![Neo4j](https://img.shields.io/badge/Neo4j-5.14-blue)

## 🎯 What is GraphRAG?

**Plain RAG** uses vector embeddings and cosine similarity to find relevant text chunks, which works well for keyword matching but struggles with understanding relationships and context.

**GraphRAG** leverages knowledge graphs to:
- Extract entities and relationships from documents
- Store them in a graph database (Neo4j)
- Traverse the graph to find connected information
- Provide richer context for better reasoning

## ✨ Features

- 📄 **Document Upload**: Upload text or PDF files for processing
- 🧠 **Entity Extraction**: Automatically extract entities and relationships using LLM (OpenAI GPT)
- 🕸️ **Graph Visualization**: Interactive visualization of the knowledge graph
- 🔍 **Dual RAG Approaches**:
  - Plain RAG: Vector similarity search over text embeddings
  - GraphRAG: Graph traversal for relationship-aware retrieval
- 📊 **Side-by-Side Comparison**: Compare answers from both approaches
- 💾 **Dual Storage**:
  - Neo4j: Graph database for entities and relationships
  - SQLite: Document storage with vector embeddings

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Tailwind CSS + Vis.js)                     │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Document  │  │     LLM      │  │     RAG      │   │
│  │  Processor  │  │   Service    │  │   Service    │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
└───────────┬──────────────────┬──────────────────────────┘
            │                  │
     ┌──────▼──────┐    ┌─────▼─────┐
     │   SQLite    │    │   Neo4j   │
     │ (Vectors +  │    │  (Graph   │
     │  Metadata)  │    │  Storage) │
     └─────────────┘    └───────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key

### Running with Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/iarslankhalid/GraphRAG.git
cd GraphRAG
```

2. **Set up environment variables**
```bash
# Copy and edit the environment file
cp backend/.env.example backend/.env

# Add your OpenAI API key to backend/.env
# OPENAI_API_KEY=your_key_here
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (username: neo4j, password: password)

### Running Locally (Development)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run the backend
python main.py
```

Backend will be available at http://localhost:8000

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

#### Neo4j

Install and run Neo4j locally or use the Docker container:
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.14.0
```

## 📖 Usage Guide

### 1. Upload a Document

- Click on the upload area in the "Upload Document" section
- Select a `.txt` or `.pdf` file
- Click "Upload and Process"
- Wait for entity and relationship extraction to complete

### 2. Visualize the Graph

- The knowledge graph will automatically update after upload
- Pan and zoom to explore entities and relationships
- Hover over nodes to see entity details
- Different colors represent different entity types

### 3. Ask Questions

- Type a question in the "Ask a Question" section
- Click "Ask" to get answers from both RAG approaches
- Compare the responses side-by-side
- Notice how GraphRAG uses relationships for better context

### Example Questions

If you upload a document about a company:
- "Who is the CEO of the company?"
- "What products does the company make?"
- "Where is the company located?"
- "What are the relationships between different departments?"

## 🔧 Configuration

### Backend Configuration (backend/.env)

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# SQLite Configuration
SQLITE_DB_PATH=./data/graphrag.db

# Application Configuration
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_SIZE=10485760
```

### Frontend Configuration (frontend/.env)

```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Example Data

Try uploading this sample text to see GraphRAG in action:

```text
TechCorp is a software company founded in 2010 by John Smith and Sarah Johnson.
The company is headquartered in San Francisco, California.

John Smith serves as the CEO and focuses on product strategy.
Sarah Johnson is the CTO and leads the engineering team.

TechCorp develops AI-powered analytics software used by Fortune 500 companies.
Their flagship product, DataInsight, processes millions of data points daily.

In 2022, TechCorp acquired StartupAI, a machine learning startup based in Boston.
This acquisition brought 50 new engineers to the team.

The company raised $100 million in Series C funding led by Venture Capital Partners.
```

Questions to try:
- "Who founded TechCorp?"
- "What does TechCorp do?"
- "Where is TechCorp located?"
- "Who leads the engineering team?"
- "What company did TechCorp acquire?"

## 🎓 How It Works

### Plain RAG Flow

1. Document is split into chunks
2. Each chunk is embedded using OpenAI's embedding model
3. Chunks are stored in SQLite with their embeddings
4. When a question is asked:
   - Question is embedded
   - Most similar chunks are found using cosine similarity
   - LLM generates answer using retrieved chunks

### GraphRAG Flow

1. Document is processed to extract entities and relationships using LLM
2. Entities are stored as nodes in Neo4j
3. Relationships are stored as edges in Neo4j
4. When a question is asked:
   - Entities mentioned in the question are identified
   - Graph neighborhood around those entities is retrieved
   - LLM generates answer using structured graph context

### Key Differences

| Aspect | Plain RAG | GraphRAG |
|--------|-----------|----------|
| **Storage** | Vector embeddings | Knowledge graph |
| **Retrieval** | Cosine similarity | Graph traversal |
| **Context** | Text chunks | Entities + Relationships |
| **Understanding** | Keyword matching | Relationship-aware |
| **Reasoning** | Surface-level | Deep structural |

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Neo4j**: Graph database for knowledge storage
- **SQLite**: Relational database for documents and embeddings
- **OpenAI GPT**: LLM for entity extraction and question answering
- **LangChain**: LLM application framework
- **PyPDF2**: PDF text extraction

### Frontend
- **React**: UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Vis.js**: Graph visualization library
- **Axios**: HTTP client
- **React Icons**: Icon library
- **Vite**: Build tool and development server

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## 📝 API Endpoints

### Documents
- `POST /api/documents/upload` - Upload and process a document
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get document by ID
- `DELETE /api/documents/{id}` - Delete a document

### Graph
- `GET /api/graph/` - Get full knowledge graph
- `GET /api/graph/entity/{id}` - Get entity neighborhood
- `GET /api/graph/search` - Search entities
- `DELETE /api/graph/` - Clear graph

### RAG
- `POST /api/rag/plain` - Ask question using Plain RAG
- `POST /api/rag/graph` - Ask question using GraphRAG
- `POST /api/rag/compare` - Compare both approaches

### Health
- `GET /api/health` - Check system health

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT and embedding models
- Neo4j for the graph database
- FastAPI for the excellent web framework
- React and Tailwind CSS teams

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ to demonstrate the power of GraphRAG**
