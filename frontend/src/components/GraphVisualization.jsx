/**
 * Graph Visualization Component
 * Displays the knowledge graph using vis-network
 */
import { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network/standalone';
import { FiRefreshCw } from 'react-icons/fi';
import { getGraph } from '../services/api';

const GraphVisualization = ({ refreshTrigger }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });
  const [error, setError] = useState(null);

  const loadGraph = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getGraph();
      
      if (!data.nodes || data.nodes.length === 0) {
        setStats({ nodes: 0, edges: 0 });
        setError('No data in knowledge graph. Upload a document to get started.');
        return;
      }

      // Prepare nodes for vis-network
      const nodes = data.nodes.map(node => ({
        id: node.id,
        label: node.name,
        title: `${node.type}: ${node.name}`,
        color: getColorForType(node.type),
        font: { color: '#333' }
      }));

      // Prepare edges for vis-network
      const edges = data.relationships
        .filter(rel => rel.type) // Filter out null types
        .map((rel, idx) => ({
          id: idx,
          from: rel.start,
          to: rel.end,
          label: rel.type,
          arrows: 'to',
          font: { align: 'middle', size: 10 }
        }));

      setStats({ nodes: nodes.length, edges: edges.length });

      // Create network
      if (containerRef.current) {
        const graphData = { nodes, edges };
        const options = {
          nodes: {
            shape: 'dot',
            size: 20,
            font: {
              size: 14,
            },
            borderWidth: 2,
            shadow: true
          },
          edges: {
            width: 2,
            color: { color: '#848484' },
            smooth: {
              type: 'continuous'
            }
          },
          physics: {
            stabilization: {
              iterations: 200
            },
            barnesHut: {
              gravitationalConstant: -8000,
              springConstant: 0.001,
              springLength: 200
            }
          },
          interaction: {
            hover: true,
            tooltipDelay: 100
          }
        };

        if (networkRef.current) {
          networkRef.current.destroy();
        }

        networkRef.current = new Network(containerRef.current, graphData, options);
      }
    } catch (err) {
      setError(err.message || 'Failed to load graph');
    } finally {
      setLoading(false);
    }
  };

  // Color scheme for different entity types
  const getColorForType = (type) => {
    const colors = {
      'Person': '#3B82F6',      // Blue
      'Organization': '#10B981', // Green
      'Location': '#F59E0B',     // Amber
      'Concept': '#8B5CF6',      // Purple
      'Event': '#EF4444',        // Red
      'Technology': '#06B6D4',   // Cyan
    };
    return colors[type] || '#6B7280'; // Default gray
  };

  useEffect(() => {
    loadGraph();
  }, [refreshTrigger]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Knowledge Graph</h2>
          <p className="text-sm text-gray-600">
            {stats.nodes} entities, {stats.edges} relationships
          </p>
        </div>
        <button
          onClick={loadGraph}
          disabled={loading}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
        >
          <FiRefreshCw className={`mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Graph container */}
      <div
        ref={containerRef}
        className="w-full h-96 border-2 border-gray-200 rounded-lg bg-gray-50"
      />

      {/* Loading state */}
      {loading && (
        <div className="mt-4 text-center text-gray-600">
          Loading graph...
        </div>
      )}

      {/* Error or empty state */}
      {error && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">{error}</p>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-sm font-semibold text-gray-700 mb-2">Entity Types:</p>
        <div className="flex flex-wrap gap-3">
          {['Person', 'Organization', 'Location', 'Concept', 'Event', 'Technology'].map(type => (
            <div key={type} className="flex items-center">
              <div
                className="w-4 h-4 rounded-full mr-1"
                style={{ backgroundColor: getColorForType(type) }}
              />
              <span className="text-xs text-gray-600">{type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;
