/**
 * API service for communicating with the backend.
 * Centralizes all HTTP requests.
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Health check endpoint
 */
export const checkHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

/**
 * Upload a document (text or PDF)
 */
export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get list of all documents
 */
export const getDocuments = async () => {
  const response = await api.get('/api/documents/');
  return response.data;
};

/**
 * Delete a document
 */
export const deleteDocument = async (documentId) => {
  const response = await api.delete(`/api/documents/${documentId}`);
  return response.data;
};

/**
 * Get the full knowledge graph
 */
export const getGraph = async () => {
  const response = await api.get('/api/graph/');
  return response.data;
};

/**
 * Search for entities in the graph
 */
export const searchEntities = async (query, limit = 10) => {
  const response = await api.get('/api/graph/search', {
    params: { query, limit }
  });
  return response.data;
};

/**
 * Ask a question using Plain RAG
 */
export const askPlainRAG = async (question) => {
  const response = await api.post('/api/rag/plain', { question });
  return response.data;
};

/**
 * Ask a question using GraphRAG
 */
export const askGraphRAG = async (question) => {
  const response = await api.post('/api/rag/graph', { question });
  return response.data;
};

/**
 * Compare Plain RAG vs GraphRAG
 */
export const compareRAG = async (question) => {
  const response = await api.post('/api/rag/compare', { question });
  return response.data;
};

export default api;
