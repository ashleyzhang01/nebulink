'use client'

import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import * as THREE from 'three';
import ForceGraph3D, { ForceGraph3DInstance } from '3d-force-graph';

interface BaseNodeObject {
    id?: string | number;
    x?: number;
    y?: number;
    z?: number;
    vx?: number;
    vy?: number;
    vz?: number;
    fx?: number;
    fy?: number;
    fz?: number;
}
  
interface PublicNode extends BaseNodeObject {
  id: string;
  type: 'linkedin_organization' | 'github_repository';
  name: string;
  description?: string;
  industry?: string;
  company_size?: string;
  user_count?: number;
  stars?: number;
  contributor_count?: number;
}

interface PublicLink {
  source: string;
  target: string;
  type: string;
}

interface PublicGraphData {
  nodes: PublicNode[];
  links: PublicLink[];
}

const PublicNetworkGraph: React.FC = () => {
  const graphRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<PublicGraphData | null>(null);
  const graphInstance = useRef<ForceGraph3DInstance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<PublicNode | null>(null);

  useEffect(() => {
    async function fetchPublicNetwork() {
      setIsLoading(true);
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/network/public');
        setGraphData(response.data);
      } catch (error) {
        console.error('Error fetching public network data:', error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchPublicNetwork();
  }, []);

  useEffect(() => {
    if (graphData && graphRef.current && !graphInstance.current) {
      initializeGraph();
    }
  }, [graphData]);

  const generateRandomColor = (type: string, userCount: number = 1) => {
    const hue = type === 'github_repository' ? 0.6 : 0.8; // Different hue based on type
    const saturation = Math.min(1, 0.5 + Math.log(userCount + 1) * 0.1); // Varies with user count
    const lightness = Math.max(0.3, Math.random() * 0.3 + 0.3); // Controlled randomness
  
    return new THREE.Color().setHSL(hue, saturation, lightness);
  };

  const initializeGraph = () => {
    if (!graphRef.current || !graphData) return;

    try {
        const Graph = ForceGraph3D()(graphRef.current)
        .graphData(graphData)
        .backgroundColor('#02020f')
        .nodeThreeObject((node) => {
            const publicNode = node as PublicNode;
            const size = publicNode.user_count ? Math.log(publicNode.user_count) + 5 : 5;
            const sphereGeometry = new THREE.SphereGeometry(size);
            const color = generateRandomColor(publicNode.type, publicNode.user_count);
            const sphereMaterial = new THREE.MeshBasicMaterial({ color: color });
            return new THREE.Mesh(sphereGeometry, sphereMaterial);
        })
        .nodeLabel((node) => {
            const publicNode = node as PublicNode;
            return `${publicNode.name}`;
        })
        .linkWidth(0.2)
        .linkOpacity(0.1)
        .onNodeClick((node) => {
          const publicNode = node as PublicNode;
          setSelectedNode(publicNode);
        });

      graphInstance.current = Graph;
      Graph.d3Force('charge')?.strength(-100);
      Graph.d3Force('center')?.strength(0.05);

      graphData.nodes.forEach(node => {
        node.x = Math.random() * 200 - 100;
        node.y = Math.random() * 200 - 100;
        node.z = Math.random() * 200 - 100;
      });

      let angle = 0;
      setInterval(() => {
        graphData.nodes.forEach((node, i) => {
          const forceStrength = 0.1;
          const fx = Math.sin(angle + i * 0.05) * forceStrength;
          const fy = Math.cos(angle + i * 0.05) * forceStrength;
          const fz = Math.sin(angle + i * 0.08) * forceStrength;
          
          node.fx = (node.x || 0) + fx;
          node.fy = (node.y || 0) + fy;
          node.fz = (node.z || 0) + fz;
        });
        angle += 0.02;
        Graph.refresh();
      }, 50);
    } catch (error) {
      console.error('Error initializing graph:', error);
    }
  };

  if (isLoading) {
    return <div>Loading public network...</div>;
  }

  return (
    <div style={{ position: 'relative', width: '100vw', height: '90vh' }}>
      <div ref={graphRef} style={{ width: '100%', height: '100%' }} />
      {selectedNode && (
        <div style={panelStyles}>
          <button onClick={() => setSelectedNode(null)} style={closeButtonStyles}>x</button>
          <h3>{selectedNode.name}</h3>
          {selectedNode.description && <p><strong>Description:</strong> {selectedNode.description}</p>}
          {selectedNode.industry && <p><strong>Industry:</strong> {selectedNode.industry}</p>}
          {selectedNode.company_size && <p><strong>Company Size:</strong> {selectedNode.company_size}</p>}
          {selectedNode.user_count && <p><strong>User Count:</strong> {selectedNode.user_count}</p>}
          {selectedNode.stars && <p><strong>Stars:</strong> {selectedNode.stars}</p>}
          {selectedNode.contributor_count && <p><strong>Contributors:</strong> {selectedNode.contributor_count}</p>}
        </div>
      )}
    </div>
  );
};

const panelStyles: React.CSSProperties = {
    position: 'absolute',
    top: '70px',
    right: '20px',
    width: '500px',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    color: 'white',
    padding: '15px',
    borderRadius: '8px',
    overflowY: 'auto',
    maxHeight: '500px',
    zIndex: 10,
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
};
  
const closeButtonStyles: React.CSSProperties = {
    position: 'absolute',
    top: '10px',
    right: '10px',
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '16px',
    cursor: 'pointer',
};

export default PublicNetworkGraph;