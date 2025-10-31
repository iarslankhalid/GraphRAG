# GraphRAG Explorer - Developer Guide

A comprehensive guide for developers working on or extending GraphRAG Explorer.

## Project Structure

```
GraphRAG/
├── backend/              # FastAPI backend
│   ├── database/        # Database managers (Neo4j, SQLite)
│   ├── models/          # Pydantic models for API
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── config.py        # Configuration management
│   └── main.py          # Application entry point
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── utils/       # Utility functions
│   └── public/          # Static assets
├── data/                # Data storage and examples
├── docker/              # Docker configurations
└── docs/                # Documentation
```

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop
- Git
- Your favorite IDE (VS Code recommended)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest black flake8 mypy

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run backend
python main.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Install dev dependencies (already in package.json)
# - eslint
# - prettier

# Set up environment
cp .env.example .env

# Run dev server
npm run dev
```

### Database Setup

```bash
# Start Neo4j with Docker
docker run -d \
  --name graphrag-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.14.0
```

## Code Style Guide

### Python (Backend)

**Follow PEP 8 with these conventions:**

```python
# Imports organized: standard library, third-party, local
import os
from typing import List, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from services.llm_service import LLMService

# Constants in UPPER_CASE
MAX_FILE_SIZE = 10485760

# Classes in PascalCase
class DocumentProcessor:
    """Clear docstrings for all classes."""
    
    def __init__(self, config: dict):
        self.config = config
    
    # Methods in snake_case
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and extract information.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing processed data
        """
        pass

# Functions in snake_case with type hints
def extract_entities(text: str) -> List[Dict[str, str]]:
    """Extract entities from text."""
    pass
```

**Key points:**
- Use type hints everywhere
- Write docstrings for all public functions/classes
- Keep functions small and focused (< 50 lines)
- Use descriptive variable names
- Comment complex logic

### JavaScript/React (Frontend)

**Modern React with hooks:**

```javascript
// Imports organized: React, third-party, local
import { useState, useEffect } from 'react';
import axios from 'axios';

import { getDocuments } from '../services/api';

// Components in PascalCase
const DocumentList = ({ onSelect }) => {
  // State and hooks at the top
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Effects
  useEffect(() => {
    loadDocuments();
  }, []);
  
  // Event handlers prefixed with 'handle'
  const handleDocumentClick = (doc) => {
    onSelect(doc);
  };
  
  // Render helpers
  const renderDocument = (doc) => (
    <div key={doc.id} onClick={() => handleDocumentClick(doc)}>
      {doc.name}
    </div>
  );
  
  // Main render
  return (
    <div className="document-list">
      {loading ? 'Loading...' : documents.map(renderDocument)}
    </div>
  );
};

export default DocumentList;
```

**Key points:**
- Use functional components with hooks
- Destructure props
- Use meaningful component names
- Add JSDoc comments for complex components
- Keep components small (< 200 lines)

## API Development

### Adding a New Endpoint

1. **Define Pydantic model** in `backend/models/schemas.py`:

```python
class NewFeatureRequest(BaseModel):
    """Request model for new feature."""
    param1: str
    param2: int = 10  # with default
```

2. **Create router** in `backend/routers/new_feature.py`:

```python
from fastapi import APIRouter, Depends
from models.schemas import NewFeatureRequest

router = APIRouter(prefix="/api/feature", tags=["feature"])

@router.post("/action")
async def perform_action(request: NewFeatureRequest):
    """Perform the action."""
    return {"result": "success"}
```

3. **Register router** in `backend/main.py`:

```python
from routers import new_feature

app.include_router(new_feature.router)
```

4. **Add API client method** in `frontend/src/services/api.js`:

```javascript
export const performAction = async (param1, param2) => {
  const response = await api.post('/api/feature/action', {
    param1,
    param2
  });
  return response.data;
};
```

## Database Development

### Adding Neo4j Queries

**In `backend/database/neo4j_manager.py`:**

```python
def get_related_entities(self, entity_id: str, relation_type: str) -> List[Dict]:
    """Get entities related by specific relationship type."""
    with self.driver.session() as session:
        query = """
            MATCH (e:Entity {id: $entity_id})-[r:%s]->(related:Entity)
            RETURN related
        """ % relation_type
        
        results = session.run(query, entity_id=entity_id)
        return [dict(record["related"]) for record in results]
```

**Best practices:**
- Use parameterized queries
- Add proper error handling
- Log query execution
- Test with Neo4j Browser first

### Adding SQLite Tables

**In `backend/database/sqlite_manager.py`:**

```python
class NewTable(Base):
    """New table for storing data."""
    __tablename__ = 'new_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Service Development

### Creating a New Service

1. **Create service file** in `backend/services/`:

```python
# backend/services/new_service.py
import logging

logger = logging.getLogger(__name__)

class NewService:
    """Service for handling new functionality."""
    
    def __init__(self, config: dict):
        self.config = config
        logger.info("NewService initialized")
    
    def process(self, data: str) -> dict:
        """Process data and return results."""
        try:
            # Implementation
            result = {"status": "success"}
            return result
        except Exception as e:
            logger.error(f"Error in NewService: {e}")
            raise
```

2. **Register as dependency** in `main.py`:

```python
new_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global new_service
    new_service = NewService(config)
    yield
    # Cleanup

def get_new_service() -> NewService:
    return new_service
```

## Component Development

### Creating a New React Component

```javascript
// frontend/src/components/NewComponent.jsx

/**
 * NewComponent - Brief description
 * 
 * Props:
 *   data: Array of items to display
 *   onItemClick: Callback when item is clicked
 *   loading: Boolean indicating loading state
 */
import { useState } from 'react';
import { FiStar } from 'react-icons/fi';

const NewComponent = ({ data = [], onItemClick, loading = false }) => {
  const [selected, setSelected] = useState(null);
  
  const handleClick = (item) => {
    setSelected(item);
    onItemClick?.(item);
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div className="new-component">
      {data.map(item => (
        <div 
          key={item.id}
          onClick={() => handleClick(item)}
          className={`item ${selected?.id === item.id ? 'selected' : ''}`}
        >
          <FiStar />
          {item.name}
        </div>
      ))}
    </div>
  );
};

export default NewComponent;
```

## Testing

### Backend Testing

```python
# backend/tests/test_document_processor.py
import pytest
from services.document_processor import DocumentProcessor

@pytest.fixture
def processor():
    return DocumentProcessor(chunk_size=100)

def test_split_text(processor):
    text = "This is a test. " * 20
    chunks = processor.split_text_into_chunks(text)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= 100 for chunk in chunks)

def test_extract_text_from_pdf(processor):
    text = processor.extract_text_from_pdf("test.pdf")
    assert text
    assert len(text) > 0
```

**Run tests:**
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend Testing

```javascript
// frontend/src/components/__tests__/NewComponent.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import NewComponent from '../NewComponent';

describe('NewComponent', () => {
  const mockData = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' }
  ];
  
  test('renders items', () => {
    render(<NewComponent data={mockData} />);
    expect(screen.getByText('Item 1')).toBeInTheDocument();
  });
  
  test('calls onItemClick when item clicked', () => {
    const handleClick = jest.fn();
    render(<NewComponent data={mockData} onItemClick={handleClick} />);
    
    fireEvent.click(screen.getByText('Item 1'));
    expect(handleClick).toHaveBeenCalledWith(mockData[0]);
  });
});
```

**Run tests:**
```bash
cd frontend
npm test
npm run test:coverage
```

## Debugging

### Backend Debugging

**With VS Code:**

`.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

**With logging:**
```python
import logging

# Set log level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug logs
logger.debug(f"Processing document: {filename}")
logger.info(f"Extracted {len(entities)} entities")
logger.error(f"Failed to process: {error}")
```

### Frontend Debugging

**Browser DevTools:**
- Use React Developer Tools extension
- Check Network tab for API calls
- Use Console for errors and logs

**Debug logging:**
```javascript
// Add conditional logging
const DEBUG = import.meta.env.DEV;

if (DEBUG) {
  console.log('Component state:', state);
}

// Use debugger statement
const handleClick = () => {
  debugger;  // Execution will pause here
  processData();
};
```

## Performance Optimization

### Backend

1. **Database connection pooling**
2. **Async operations** where possible
3. **Caching** frequent queries
4. **Batch processing** for LLM calls
5. **Index optimization** in Neo4j

### Frontend

1. **Code splitting** with dynamic imports
2. **Memoization** with useMemo/useCallback
3. **Lazy loading** components
4. **Debouncing** user input
5. **Image optimization**

## Common Tasks

### Adding a New Entity Type

1. Update prompt in `llm_service.py`
2. Add color in `GraphVisualization.jsx`
3. Update documentation

### Changing LLM Model

1. Edit `backend/config.py`:
```python
openai_model: str = "gpt-4"
```

2. Restart backend

### Adding New File Type Support

1. Add handler in `document_processor.py`:
```python
def extract_text_from_docx(self, path: str) -> str:
    # Implementation
    pass
```

2. Update upload validation
3. Update documentation

## Deployment Checklist

- [ ] Set production environment variables
- [ ] Update CORS origins
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backup
- [ ] Test with production data
- [ ] Update API rate limits
- [ ] Review security settings
- [ ] Set up CI/CD pipeline
- [ ] Update documentation

## Useful Commands

```bash
# Backend
cd backend
pip install -r requirements.txt  # Install deps
python main.py                   # Run server
pytest                          # Run tests
black .                         # Format code
flake8 .                        # Lint code

# Frontend
cd frontend
npm install                     # Install deps
npm run dev                     # Dev server
npm run build                   # Build for prod
npm test                        # Run tests
npm run lint                    # Lint code

# Docker
docker-compose up -d            # Start all services
docker-compose down             # Stop all services
docker-compose logs -f          # View logs
docker-compose ps               # Check status

# Neo4j
# Access browser at http://localhost:7474
# Query examples in Neo4j Browser
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Neo4j Cypher Reference](https://neo4j.com/docs/cypher-manual/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Tailwind CSS](https://tailwindcss.com/docs)

## Getting Help

- Check existing issues on GitHub
- Review code comments
- Read the documentation
- Ask in discussions

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

---

Happy coding! 🚀
