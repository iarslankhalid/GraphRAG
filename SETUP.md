# GraphRAG Explorer - Setup Guide

This guide will walk you through setting up the GraphRAG Explorer application.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** (for backend)
- **Node.js 18+** and npm (for frontend)
- **Docker and Docker Compose** (recommended for easy setup)
- **OpenAI API Key** (required for LLM and embeddings)

## Option 1: Docker Setup (Recommended)

This is the easiest way to get started.

### Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (you won't be able to see it again)

### Step 2: Configure Environment

```bash
# Clone the repository
git clone https://github.com/iarslankhalid/GraphRAG.git
cd GraphRAG

# Set up backend environment
cp backend/.env.example backend/.env

# Edit backend/.env and add your OpenAI API key
nano backend/.env  # or use any text editor
```

In `backend/.env`, set:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Start the Application

```bash
# Start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

### Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474
  - Username: `neo4j`
  - Password: `password`

### Step 5: Test the Application

1. Open http://localhost:3000 in your browser
2. Upload the example file from `data/example_document.txt`
3. Wait for processing to complete
4. View the knowledge graph
5. Try asking questions!

### Stopping the Application

```bash
docker-compose down

# To also remove volumes (clears all data)
docker-compose down -v
```

## Option 2: Local Development Setup

For development or if you prefer not to use Docker.

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Create data directory
mkdir -p data/uploads

# Run the backend
python main.py
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

### Neo4j Setup

You need Neo4j running locally. The easiest way is with Docker:

```bash
docker run -d \
  --name graphrag-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.14.0
```

Or download and install Neo4j Desktop from https://neo4j.com/download/

## Troubleshooting

### Backend won't start

**Error: "Failed to connect to Neo4j"**
- Make sure Neo4j is running
- Check that Neo4j is accessible at `bolt://localhost:7687`
- Verify username and password in `.env`

**Error: "Invalid OpenAI API key"**
- Ensure your API key is correct in `backend/.env`
- Check that your OpenAI account has credits

**Error: "Module not found"**
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Activate your virtual environment

### Frontend won't start

**Error: "Cannot connect to backend"**
- Make sure the backend is running at http://localhost:8000
- Check that `VITE_API_URL` in `frontend/.env` is correct

**Error: "Module not found"**
- Make sure you've installed all dependencies: `npm install`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again

### Docker issues

**Error: "Port already in use"**
- Another service is using one of the required ports (3000, 8000, 7474, 7687)
- Stop the conflicting service or change the port in `docker-compose.yml`

**Error: "Cannot connect to Docker daemon"**
- Make sure Docker Desktop is running
- On Linux, ensure your user is in the docker group: `sudo usermod -aG docker $USER`

### Graph visualization is empty

- Make sure you've uploaded a document first
- Check that entity extraction completed successfully
- Look for errors in the backend logs

### Questions return no results

- Ensure you have uploaded and processed at least one document
- Check that OpenAI API key is working
- Verify there are entities in the graph (check Neo4j browser)

## Performance Considerations

### OpenAI API Costs

- Entity extraction: ~$0.002 per 1000 tokens (GPT-3.5-turbo)
- Embeddings: ~$0.0001 per 1000 tokens
- Question answering: ~$0.002 per 1000 tokens

A typical 1000-word document costs about $0.05-0.10 to process.

### Rate Limits

- OpenAI free tier: 3 requests/minute
- OpenAI paid tier: Higher limits based on usage

If you hit rate limits, wait a minute between uploads.

## Next Steps

1. Read the main README.md for usage guide
2. Try the example document in `data/example_document.txt`
3. Explore the API documentation at http://localhost:8000/docs
4. Experiment with different questions to see the difference between Plain RAG and GraphRAG

## Getting Help

- Check the logs: `docker-compose logs` or `python main.py`
- Review the API documentation at http://localhost:8000/docs
- Open an issue on GitHub

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
