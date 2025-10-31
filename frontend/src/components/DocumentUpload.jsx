/**
 * Document Upload Component
 * Allows users to upload text or PDF files for processing
 */
import { useState } from 'react';
import { FiUpload, FiFile, FiCheckCircle } from 'react-icons/fi';
import { uploadDocument } from '../services/api';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['text/plain', 'application/pdf'];
      if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.txt')) {
        setError('Please select a .txt or .pdf file');
        return;
      }
      setFile(selectedFile);
      setError(null);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await uploadDocument(file);
      setUploadResult(result);
      setFile(null);
      
      // Notify parent component
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Upload Document</h2>
      <p className="text-gray-600 mb-6">
        Upload a text or PDF file to extract entities and build the knowledge graph
      </p>

      {/* File input */}
      <div className="mb-4">
        <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
          <input
            type="file"
            accept=".txt,.pdf,text/plain,application/pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={uploading}
          />
          <div className="text-center">
            <FiUpload className="mx-auto text-4xl text-gray-400 mb-2" />
            <span className="text-gray-600">
              {file ? file.name : 'Click to select a file'}
            </span>
          </div>
        </label>
      </div>

      {/* Selected file info */}
      {file && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg flex items-center justify-between">
          <div className="flex items-center">
            <FiFile className="text-blue-600 mr-2" />
            <span className="text-sm text-gray-700">{file.name}</span>
            <span className="text-xs text-gray-500 ml-2">
              ({(file.size / 1024).toFixed(2)} KB)
            </span>
          </div>
          <button
            onClick={() => setFile(null)}
            className="text-red-500 hover:text-red-700"
          >
            Remove
          </button>
        </div>
      )}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className={`w-full py-3 rounded-lg font-semibold transition-colors ${
          !file || uploading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {uploading ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
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
          </span>
        ) : (
          'Upload and Process'
        )}
      </button>

      {/* Error message */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Success message */}
      {uploadResult && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center mb-2">
            <FiCheckCircle className="text-green-600 mr-2" />
            <span className="font-semibold text-green-800">Upload Successful!</span>
          </div>
          <div className="text-sm text-gray-700 space-y-1">
            <p>• File: {uploadResult.filename}</p>
            <p>• Entities extracted: {uploadResult.entities_extracted}</p>
            <p>• Relationships extracted: {uploadResult.relationships_extracted}</p>
            <p>• Chunks created: {uploadResult.chunks_created}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
