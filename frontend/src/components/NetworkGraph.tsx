"use client";
import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import ForceGraph3D from '3d-force-graph';

interface NodeObject {
  id?: string | number;
  index?: number;
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

interface Node extends NodeObject {
  id: string;
  profile_picture?: string;
  individual_name: string;
  group_name: string;
  summarized_description: string;
  comprehensive_description?: string;
  email?: string;
  link?: string;
  expanded?: boolean;
  corresponding_node?: string;
  color?: string;
}

interface Link {
  source: string;
  target: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

const NetworkGraph: React.FC = () => {
  const graphRef = useRef<HTMLDivElement | null>(null);
  const modalRef = useRef<HTMLDivElement | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [activatedGroupName, setActivatedGroupName] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    // Load nodes and links from JSON files
    Promise.all([
      fetch('/dummy_data/dummy_nodes.json').then(response => response.json()),
      fetch('/dummy_data/dummy_links.json').then(response => response.json())
    ])
    .then(([nodesData, linksData]) => {
      setGraphData({ nodes: nodesData, links: linksData });
    })
    .catch(error => console.error('Error loading the JSON files:', error));
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined' && graphData && graphRef.current) {
      const Graph = ForceGraph3D()(graphRef.current)
        .graphData(graphData)
        .backgroundColor('#000022')
        .nodeAutoColorBy('group_name')
        .linkWidth(2)
        .nodeVal(1)
        .nodeThreeObject((node: NodeObject) => {
          const typedNode = node as Node;
        
          if (typedNode.expanded) {
            const nodeGroup = new THREE.Group();
        
            const sphereGeometry = new THREE.SphereGeometry(5);
            const sphereMaterial = new THREE.MeshBasicMaterial({ color: typedNode.color || 'lightblue' });
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            nodeGroup.add(sphere);
        
            if (typedNode.profile_picture) {
              const imgTexture = new THREE.TextureLoader().load(typedNode.profile_picture);
              const imgMaterial = new THREE.SpriteMaterial({ map: imgTexture });
              const sprite = new THREE.Sprite(imgMaterial);
              sprite.scale.set(20, 20, 1);
              sprite.position.set(-15, 10, 0);
              nodeGroup.add(sprite);
            }
        
            const labelText = `${typedNode.individual_name}\n${typedNode.group_name}\n${typedNode.summarized_description}`;
            const label = createTextSprite(labelText, { fontsize: 50 });
            label.position.set(-15, 10, 0);
            nodeGroup.add(label);
        
            return nodeGroup;
          } else {
            const sphereGeometry = new THREE.SphereGeometry(5);
            const sphereMaterial = new THREE.MeshBasicMaterial({ color: typedNode.color || 'lightblue' });
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            return sphere;
          }
        })
      
      
        .onNodeClick((node: object) => { // graph geometry changes each time we add something like text and picture so it moves away from original position
          const typedNode = node as Node;
          if (activatedGroupName === null || activatedGroupName !== typedNode.group_name) {
            setActivatedGroupName(typedNode.group_name);
            expandGroupNodes(typedNode.group_name);
            const groupNodeIds = getGroupNodeIds(typedNode.group_name);
            Graph.zoomToFit(1000, 50, (n: object) => groupNodeIds.includes((n as Node).id));
            Graph.refresh();
          } else {
            setSelectedNode(typedNode);
            showNodeModal();
          }
        })
        .onBackgroundClick(() => {
          setActivatedGroupName(null);
          expandGroupNodes(null);
          Graph.refresh();
        });

      const getGroupNodeIds = (groupName: string) => {
        return graphData?.nodes.filter(n => n.group_name === groupName).map(n => n.id) || [];
      };

      const createTextSprite = (message: string, parameters: { fontsize: number }) => {
        const fontface = 'Arial';
        const fontsize = parameters.fontsize || 18;
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        if (!context) {
          throw new Error('Failed to get 2D context');
        }

        context.font = `${fontsize}px ${fontface}`;
        const lines = message.split('\n');
        const textWidth = Math.max(...lines.map(line => context.measureText(line).width));
        const lineHeight = fontsize * 1.4;

        canvas.width = textWidth + 8;
        canvas.height = lineHeight * lines.length + 8;

        context.font = `${fontsize}px ${fontface}`;
        context.fillStyle = 'white';
        context.textBaseline = 'top';

        lines.forEach((line, index) => {
          context.fillText(line, 4, 4 + lineHeight * index);
        });

        const texture = new THREE.CanvasTexture(canvas);
        texture.needsUpdate = true;
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(canvas.width / 15, canvas.height / 15, 1.0);

        return sprite;
      };
    }
  }, [graphData, activatedGroupName]);

  const showNodeModal = () => {
    if (modalRef.current) {
      modalRef.current.style.display = 'block';
    }
  };
  

  const closeModal = () => {
    if (modalRef.current) {
      modalRef.current.style.display = 'none';
    }
    setSelectedNode(null);
  };

  const expandGroupNodes = (groupName: string | null) => {
    setGraphData(prevData => {
      if (!prevData) return null;
      return {
        ...prevData,
        nodes: prevData.nodes.map(node => ({
          ...node,
          expanded: groupName !== null && node.group_name === groupName
        }))
      };
    });
  };

  const handleCorrespondingNodeClick = () => {
    if (selectedNode?.corresponding_node) {
      const correspondingNode = graphData?.nodes.find(node => node.id === selectedNode.corresponding_node);
      if (correspondingNode && graphRef.current) {
        closeModal();
        setActivatedGroupName(correspondingNode.group_name);
        expandGroupNodes(correspondingNode.group_name);
        setSelectedNode(null);
  
        const Graph = ForceGraph3D()(graphRef.current);
  
        const x = correspondingNode.x ?? 0;
        const y = correspondingNode.y ?? 0;
        const z = correspondingNode.z ?? 0;
  
        Graph.cameraPosition(
          { x, y, z: z + 100 },
          { x, y, z },
          3000 
        );

      }
    }
  };
  
  

  return (
    <div>
      <div ref={graphRef} style={{ width: '100vw', height: '100vh' }}></div>
      {selectedNode && (
        <div id="node-modal" ref={modalRef} style={modalStyles}>
          <button onClick={closeModal} style={closeButtonStyles}>Close</button>
          <div id="modal-content" style={modalContentStyles}>
              {selectedNode.profile_picture && (
                <img
                  src={selectedNode.profile_picture}
                  alt={`${selectedNode.individual_name}'s profile`}
                  style={profilePictureModalStyles}
                />
              )}
              <div>
                <h2>{selectedNode.individual_name}</h2>
                <h3>{selectedNode.group_name}</h3>
                <p>{selectedNode.comprehensive_description}</p>
                {selectedNode.email && (
                  <p>Email: <a href={`mailto:${selectedNode.email}`} style={{ color: '#fff' }}>{selectedNode.email}</a></p>
                )}
                {selectedNode.link && (
                  <p><a href={selectedNode.link} target="_blank" rel="noopener noreferrer" style={{ color: '#fff' }}>Visit Profile</a></p>
                )}
                {selectedNode.corresponding_node && (
                  <button onClick={handleCorrespondingNodeClick} style={{ color: '#fff', background: 'none', border: 'none', cursor: 'pointer' }}>Go to Corresponding Node</button>
                )}
              </div>
            </div>
        </div>
      )}
    </div>
  );
};

const modalStyles: React.CSSProperties = {
  display: 'block',
  position: 'fixed',
  top: '10%',
  left: '50%',
  transform: 'translateX(-50%)',
  width: '60%',
  backgroundColor: 'rgba(50, 50, 50, 0.8)', // Translucent gray background
  borderRadius: '15px',
  color: '#fff',
  padding: '20px',
  boxSizing: 'border-box',
  zIndex: 1000,
  overflow: 'auto', // Allow scrolling if content overflows
  fontFamily: "'Helvetica Neue', Arial, sans-serif",
  textAlign: 'left',
};

const modalContentStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
};

const profilePictureModalStyles: React.CSSProperties = {
  width: '100px',
  height: '100px',
  borderRadius: '50%',
  marginRight: '20px',
};


const closeButtonStyles: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  color: '#fff',
  fontSize: '18px',
  cursor: 'pointer',
  position: 'absolute',
  top: '10px',
  right: '10px'
};
export default NetworkGraph;
