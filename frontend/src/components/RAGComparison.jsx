/**
 * RAG Comparison Component
 * Shows side-by-side comparison of Plain RAG vs GraphRAG answers
 */
import { useState } from 'react';
import { FiSend, FiSearch } from 'react-icons/fi';
import { compareRAG } from '../services/api';

const RAGComparison = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await compareRAG(question);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get answer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Ask a Question - Compare RAG Approaches
      </h2>
      <p className="text-gray-600 mb-6">
        See how Plain RAG (vector similarity) compares to GraphRAG (graph traversal) in answering your questions
      </p>

      {/* Question input form */}
      <form onSubmit={handleAskQuestion} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className={`px-6 py-3 rounded-lg font-semibold transition-colors flex items-center ${
              loading || !question.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Processing...
              </>
            ) : (
              <>
                <FiSend className="mr-2" />
                Ask
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Results - Side by side comparison */}
      {result && (
        <div className="space-y-6">
          {/* Question */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="font-semibold text-blue-900 mb-1">Question:</p>
            <p className="text-gray-800">{result.question}</p>
          </div>

          {/* Comparison Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Plain RAG Result */}
            <div className="border-2 border-gray-300 rounded-lg p-5 bg-gradient-to-br from-gray-50 to-white">
              <div className="flex items-center mb-3">
                <FiSearch className="text-gray-600 text-xl mr-2" />
                <h3 className="text-lg font-bold text-gray-800">Plain RAG</h3>
              </div>
              <p className="text-xs text-gray-600 mb-3 italic">
                Vector Similarity Search
              </p>
              
              <div className="mb-4">
                <p className="font-semibold text-sm text-gray-700 mb-2">Answer:</p>
                <p className="text-gray-800 leading-relaxed">
                  {result.plain_rag.answer}
                </p>
              </div>

              {result.plain_rag.chunks_used && result.plain_rag.chunks_used.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="font-semibold text-sm text-gray-700 mb-2">
                    Context Used ({result.plain_rag.chunks_used.length} chunks):
                  </p>
                  <div className="space-y-2">
                    {result.plain_rag.chunks_used.map((chunk, idx) => (
                      <div key={idx} className="text-xs bg-white p-2 rounded border border-gray-200">
                        <p className="text-gray-600 truncate">{chunk.text}</p>
                        <p className="text-gray-500 mt-1">
                          Similarity: {(chunk.similarity * 100).toFixed(1)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* GraphRAG Result */}
            <div className="border-2 border-blue-500 rounded-lg p-5 bg-gradient-to-br from-blue-50 to-white">
              <div className="flex items-center mb-3">
                <svg className="text-blue-600 text-xl mr-2" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="3" strokeWidth="2" />
                  <circle cx="6" cy="6" r="2" strokeWidth="2" />
                  <circle cx="18" cy="6" r="2" strokeWidth="2" />
                  <circle cx="6" cy="18" r="2" strokeWidth="2" />
                  <circle cx="18" cy="18" r="2" strokeWidth="2" />
                  <line x1="9" y1="10.5" x2="9.5" y2="10" strokeWidth="2" />
                  <line x1="15" y1="10" x2="14.5" y2="10.5" strokeWidth="2" />
                  <line x1="9.5" y1="14" x2="9" y2="13.5" strokeWidth="2" />
                  <line x1="14.5" y1="13.5" x2="15" y2="14" strokeWidth="2" />
                </svg>
                <h3 className="text-lg font-bold text-blue-800">GraphRAG</h3>
              </div>
              <p className="text-xs text-blue-700 mb-3 italic">
                Graph Traversal & Relationships
              </p>
              
              <div className="mb-4">
                <p className="font-semibold text-sm text-gray-700 mb-2">Answer:</p>
                <p className="text-gray-800 leading-relaxed">
                  {result.graph_rag.answer}
                </p>
              </div>

              {result.graph_rag.entities_used && result.graph_rag.entities_used.length > 0 && (
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <p className="font-semibold text-sm text-gray-700 mb-2">
                    Entities Used ({result.graph_rag.entities_used.length}):
                  </p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {result.graph_rag.entities_used.slice(0, 5).map((entity, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {entity.name}
                      </span>
                    ))}
                    {result.graph_rag.entities_used.length > 5 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        +{result.graph_rag.entities_used.length - 5} more
                      </span>
                    )}
                  </div>
                  
                  {result.graph_rag.relationships_used && result.graph_rag.relationships_used.length > 0 && (
                    <>
                      <p className="font-semibold text-sm text-gray-700 mb-2">
                        Relationships: {result.graph_rag.relationships_used.length}
                      </p>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Key Insights */}
          <div className="p-5 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
            <h3 className="font-bold text-lg text-purple-900 mb-3">
              🔍 Key Differences
            </h3>
            <div className="space-y-2 text-sm text-gray-700">
              <p><strong>Plain RAG:</strong> {result.comparison.plain_uses}</p>
              <p><strong>GraphRAG:</strong> {result.comparison.graph_uses}</p>
              <p className="pt-2 border-t border-purple-200 mt-3">
                <strong>Why GraphRAG is Better:</strong> {result.comparison.key_difference}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RAGComparison;
