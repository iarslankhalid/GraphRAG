/**
 * GraphRAG Explorer - Main Application Component
 * Demonstrates the difference between Plain RAG and GraphRAG
 */
import { useState, useEffect } from 'react';
import { FiActivity } from 'react-icons/fi';
import DocumentUpload from './components/DocumentUpload';
import GraphVisualization from './components/GraphVisualization';
import RAGComparison from './components/RAGComparison';
import { checkHealth } from './services/api';

function App() {
  const [refreshGraph, setRefreshGraph] = useState(0);
  const [healthStatus, setHealthStatus] = useState(null);

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        const health = await checkHealth();
        setHealthStatus(health);
      } catch (err) {
        setHealthStatus({ status: 'error', message: 'Cannot connect to backend' });
      }
    };

    checkBackendHealth();
  }, []);

  // Trigger graph refresh when document is uploaded
  const handleUploadSuccess = () => {
    setRefreshGraph(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mr-4">
                <FiActivity className="text-white text-2xl" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">
                  GraphRAG Explorer
                </h1>
                <p className="text-sm text-gray-600">
                  Compare Plain RAG vs GraphRAG for intelligent question answering
                </p>
              </div>
            </div>
            
            {/* Health Status */}
            {healthStatus && (
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  healthStatus.status === 'healthy' 
                    ? 'bg-green-500' 
                    : healthStatus.status === 'degraded'
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`} />
                <span className="text-sm text-gray-600">
                  {healthStatus.status === 'healthy' 
                    ? 'System Operational' 
                    : healthStatus.message}
                </span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Introduction */}
        <div className="mb-8 p-6 bg-white rounded-lg shadow-md border-l-4 border-blue-600">
          <h2 className="text-xl font-bold text-gray-800 mb-3">
            Welcome to GraphRAG Explorer! 🚀
          </h2>
          <div className="text-gray-700 space-y-2">
            <p>
              This demo showcases the power of <strong>GraphRAG</strong> compared to traditional <strong>Plain RAG</strong>.
            </p>
            <div className="grid md:grid-cols-2 gap-4 mt-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">📄 Plain RAG</h3>
                <p className="text-sm text-gray-600">
                  Uses vector embeddings and cosine similarity to find relevant text chunks. 
                  Good for simple keyword matching but misses relationships.
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-800 mb-2">🕸️ GraphRAG</h3>
                <p className="text-sm text-gray-700">
                  Leverages knowledge graphs to understand entities and their relationships. 
                  Provides richer context and better reasoning through graph traversal.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* How to Use */}
        <div className="mb-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
          <h2 className="text-lg font-bold text-purple-900 mb-3">
            📝 How to Use:
          </h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li><strong>Upload a Document:</strong> Start by uploading a text or PDF file below</li>
            <li><strong>View the Graph:</strong> See the extracted entities and relationships visualized</li>
            <li><strong>Ask Questions:</strong> Compare how both RAG approaches answer your questions</li>
            <li><strong>Observe:</strong> Notice how GraphRAG uses structural context for better answers</li>
          </ol>
        </div>

        {/* Document Upload Section */}
        <div className="mb-8">
          <DocumentUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Graph Visualization Section */}
        <div className="mb-8">
          <GraphVisualization refreshTrigger={refreshGraph} />
        </div>

        {/* RAG Comparison Section */}
        <div className="mb-8">
          <RAGComparison />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            GraphRAG Explorer - Demonstrating the power of knowledge graphs in RAG systems
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Built with FastAPI, React, Tailwind CSS, Neo4j, and OpenAI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
