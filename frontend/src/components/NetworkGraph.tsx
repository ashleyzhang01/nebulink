"use client";
import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import ForceGraph3D, { ForceGraph3DInstance } from '3d-force-graph';
import axios from 'axios';

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


interface ApiResponse {
  nodes: Node[];
  groups: Group[];
}

interface ExtendedGroup extends THREE.Group {
  __glowSphere?: THREE.Mesh;
}

interface Node extends BaseNodeObject {
  id: number;
  is_linkedin: boolean;
  username: string;
  individual_name: string | null;
  header: string | null;
  email: string | null;
  profile_picture: string | null;
  link: string;
  connection_order: number;
  corresponding_user_nodes: number[];
  group_id?: string;
  expanded?: boolean;
  color?: string;
}

interface Link {
  source: number;
  target: number;
}

interface Group {
  id: string;
  name: string;
  description: string;
  is_linkedin: boolean;
  stars?: number | null;  
  link: string;
  logo_url?: string | null;
  industry?: string | null;
  company_size?: string | null;
  headquarters?: string | null;
  specialties?: string | null;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
  groups: Group[];
}

const NetworkGraph: React.FC = () => {
  const graphRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const graphInstance = useRef<ForceGraph3DInstance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as any)) {
        setIsPanelOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    async function fetchNetwork() {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/network', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log(response.data);
        if (response.data && response.data.nodes && response.data.groups) {
          const transformedData = transformApiData(response.data);
          setGraphData(transformedData);
        } else {
          console.error('Invalid data structure received:', response.data);
          setGraphData(null);
        }
      } catch (error) {
        console.error('Error fetching network:', error);
        setGraphData(null);
      } finally {
        setIsLoading(false);
      }
    }

    fetchNetwork()
  }, [])

  const transformApiData = (apiData: ApiResponse): GraphData => {
    const links: Link[] = [];
    apiData.nodes.forEach(node => {
      node.corresponding_user_nodes.forEach(correspondingNodeId => {
        links.push({
          source: node.id,
          target: correspondingNodeId
        });
      });
    });

    return {
      nodes: apiData.nodes,
      links: links,
      groups: apiData.groups
    };
  };

  useEffect(() => {
    if (graphData && graphRef.current && !graphInstance.current) {
      initializeGraph();
    }
  }, [graphData]);

  const getNodeObjectById = (id: number | string): ExtendedGroup | undefined => {
    if (!graphInstance.current) return undefined;
    const nodeData = graphData?.nodes.find(n => n.id === id);
    if (!nodeData) return undefined;
    const nodeThreeObject = graphInstance.current.nodeThreeObject();
    if (typeof nodeThreeObject === 'function') {
      return nodeThreeObject(nodeData as Node) as ExtendedGroup;
    }
    return undefined;
  };

  const initializeGraph = () => {
    if (!graphData || !graphRef.current) return;

    try {
      // Check for WebGL support
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

      if (!gl) {
        throw new Error('WebGL not supported');
      }

      const Graph = ForceGraph3D()(graphRef.current)
        .graphData(graphData)
        .backgroundColor('#02020f')
        .nodeAutoColorBy('group_id')
        .linkWidth(0.15)
        .linkOpacity(0.12)
        .nodeThreeObject((node) => {
          const typedNode = node as Node;
          if (typedNode.expanded) {
            const nodeGroup: ExtendedGroup = new THREE.Group();

            const baseSize = typedNode.connection_order === 0 ? 3 : 1 + Math.random() * 2;

            const baseColor = new THREE.Color(typedNode.color || 'lightblue');
            const hsl = { h: 0, s: 0, l: 0 };
            baseColor.getHSL(hsl);

            // Vary the saturation and lightness slightly
            const variedColor = new THREE.Color().setHSL(
              hsl.h,
              Math.max(0, Math.min(1, hsl.s + (Math.random() - 0.5) * 0.2)),
              Math.max(0, Math.min(1, hsl.l + (Math.random() - 0.5) * 0.2))
            );

            const sphereGeometry = new THREE.SphereGeometry(baseSize);
            const sphereMaterial = new THREE.MeshBasicMaterial({ color: variedColor });
            const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
            nodeGroup.add(sphere);

            const glowGeometry = new THREE.SphereGeometry(7);
            const glowMaterial = new THREE.MeshBasicMaterial({ 
              color: typedNode.color || 'lightblue',
              transparent: true,
              opacity: 0.3
            });
            const glowSphere = new THREE.Mesh(glowGeometry, glowMaterial);
            nodeGroup.add(glowSphere);

            nodeGroup.__glowSphere = glowSphere;

            if (typedNode.profile_picture) {
              const imgTexture = new THREE.TextureLoader().load(typedNode.profile_picture);
              const imgMaterial = new THREE.SpriteMaterial({ map: imgTexture });
              const sprite = new THREE.Sprite(imgMaterial);
              sprite.scale.set(10, 10, 1);
              sprite.position.set(-15, 10, 0);
              nodeGroup.add(sprite);
            }

            const group = graphData?.groups.find(g => g.id === typedNode.group_id);
            const labelText = `${typedNode.individual_name}\n${group?.name}\n${group?.description}`;
            const label = createTextSprite(labelText, { fontsize: 24 });
            if (label) {
              label.position.set(15, -10, 0);
              nodeGroup.add(label);
            }

            return nodeGroup;
          } else {
            const sphereGeometry = new THREE.SphereGeometry(5);
            const sphereMaterial = new THREE.MeshBasicMaterial({ color: typedNode.color || 'lightblue' });
            return new THREE.Mesh(sphereGeometry, sphereMaterial);
          }
        })
        .onNodeClick((node, event) => {
          const typedNode = node as Node;
          setSelectedNode(typedNode);
          setIsPanelOpen(true);
          
          graphData.nodes.forEach(n => {
            const nodeObject = getNodeObjectById(n.id);
            if (nodeObject && nodeObject.__glowSphere) {
              (nodeObject.__glowSphere.material as THREE.MeshBasicMaterial).opacity = 0.3;
              nodeObject.__glowSphere.scale.set(1, 1, 1);
            }
          });

          const nodeObject = getNodeObjectById(typedNode.id);
          if (nodeObject && nodeObject.__glowSphere) {
            (nodeObject.__glowSphere.material as THREE.MeshBasicMaterial).opacity = 0.7;
            nodeObject.__glowSphere.scale.set(1.5, 1.5, 1.5);
          }

          const x = typedNode.x ?? 0;
          const y = typedNode.y ?? 0;
          const z = typedNode.z ?? 0;
          Graph.cameraPosition(
            { x, y, z: z + 100 },
            { x, y, z },
            1000
          );
        })
        .onBackgroundClick(() => {
          setSelectedNode(null);
          setIsPanelOpen(false);
        });

        let angle = 0;
        setInterval(() => {
          graphData.nodes.forEach((node, i) => {
            const nodeObject = getNodeObjectById(node.id);
            if (nodeObject && nodeObject.__glowSphere) {
              // Subtle size pulsing
              const scale = 1 + Math.sin(angle + i * 0.1) * 0.05;
              nodeObject.scale.set(scale, scale, scale);

              // Subtle glow opacity change
              const glowOpacity = 0.3 + Math.sin(angle + i * 0.1) * 0.1;
              (nodeObject.__glowSphere.material as THREE.MeshBasicMaterial).opacity = glowOpacity;

              // Apply small force to create gentle movement
              const forceStrength = 0.1;
              const fx = Math.sin(angle + i * 0.05) * forceStrength;
              const fy = Math.cos(angle + i * 0.05) * forceStrength;
              const fz = Math.sin(angle + i * 0.08) * forceStrength;
              
              Graph.d3Force('charge')?.strength(-50);
              Graph.d3Force('center')?.strength(0.05);
              
              node.fx = (node.x || 0) + fx;
              node.fy = (node.y || 0) + fy;
              node.fz = (node.z || 0) + fz;
            }
          });
          angle += 0.02;
          Graph.refresh();
        }, 50);

        Graph.d3Force('charge')?.strength(-100);
        Graph.d3Force('link')?.distance((link: any) => {
          const sourceNode = graphData.nodes.find(n => n.id === link.source);
          const targetNode = graphData.nodes.find(n => n.id === link.target);
          if (sourceNode && targetNode && sourceNode.group_id === targetNode.group_id) {
            return 100; 
          }
          return 50; // Default distance for other links
        });
        Graph.d3Force('center', null);
        Graph.d3Force('group', forceGroup);

        const initialNode = graphData.nodes.find(n => n.id === 0);
        if (initialNode && initialNode.x && initialNode.y && initialNode.z) {
          const distance = 200; // Adjust this value to change the initial zoom level
          Graph.cameraPosition(
            { x: initialNode.x, y: initialNode.y, z: initialNode.z + distance },
            { x: initialNode.x, y: initialNode.y, z: initialNode.z },
            2000
          );
        }

        graphInstance.current = Graph;
    } catch (error) {
      console.error('Error initializing graph:', error);
    }
    
  };

    const forceGroup = (alpha: number) => {
      const groups: { [key: string]: { x: number, y: number, z: number, count: number } } = {};
      
      graphData?.nodes.forEach(node => {
        if (node.group_id) {
          if (!groups[node.group_id]) {
            groups[node.group_id] = { x: 0, y: 0, z: 0, count: 0 };
          }
          groups[node.group_id].x += node.x || 0;
          groups[node.group_id].y += node.y || 0;
          groups[node.group_id].z += node.z || 0;
          groups[node.group_id].count++;
        }
      });
  
      Object.keys(groups).forEach(groupId => {
        const group = groups[groupId];
        group.x /= group.count;
        group.y /= group.count;
        group.z /= group.count;
      });
  
      graphData?.nodes.forEach(node => {
        if (node.group_id && groups[node.group_id]) {
          const group = groups[node.group_id];
          node.vx = (node.vx || 0) + (group.x - (node.x || 0)) * alpha;
          node.vy = (node.vy || 0) + (group.y - (node.y || 0)) * alpha;
          node.vz = (node.vz || 0) + (group.z - (node.z || 0)) * alpha;
        }
      });
    };

    function expandGroupNodes(groupId: string | null) {
      if (!graphData) return;
      setGraphData(prevData => {
        if (!prevData) return null;
        return {
          ...prevData,
          nodes: prevData.nodes.map(node => ({
            ...node,
            expanded: node.group_id === groupId
          }))
        };
      });
    }

    function getGroupNodeIds(groupId: string) {
      return graphData?.nodes?.filter(n => n.group_id === groupId)
                            .map(n => n.id) ?? [];
    }

    function createTextSprite(message: string, parameters: any = {}): THREE.Sprite {
      const fontface = parameters.fontface || 'Arial';
      const fontsize = parameters.fontsize || 18;
      const borderThickness = parameters.borderThickness || 4;
      const textColor = parameters.textColor || { r: 255, g: 255, b: 255, a: 1.0 };

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;

      context.font = `${fontsize}px ${fontface}`;

      const lines = message.split('\n');
      const lineHeight = fontsize * 1.4;
      const textWidth = Math.max(...lines.map(line => context.measureText(line).width));

      canvas.width = textWidth + borderThickness * 2;
      canvas.height = lineHeight * lines.length + borderThickness * 2;

      context.font = `${fontsize}px ${fontface}`;
      context.textBaseline = 'top';

      if (Array.isArray(lines)) {
        lines.forEach((line, index) => {
          if (index === 0) {
            context.font = `Bold ${fontsize}px ${fontface}`;
          } else {
            context.font = `${fontsize}px ${fontface}`;
          }
          context.fillStyle = `rgba(${textColor.r},${textColor.g},${textColor.b},${textColor.a})`;
          context.fillText(line, borderThickness, borderThickness + lineHeight * index);
        });
      }

      const texture = new THREE.CanvasTexture(canvas);
      texture.minFilter = THREE.LinearFilter;
      const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
      const sprite = new THREE.Sprite(spriteMaterial);
      sprite.scale.set(canvas.width / 15, canvas.height / 15, 1.0);

      return sprite;
    }

    function showNodeModal(node: Node) {
      setSelectedNode(node);
    }

    function closeModal() {
      setSelectedNode(null);
    }
  
    function handleCorrespondingNodeClick(nodeId: number) {
      if (graphData && graphInstance.current) {
        const targetNode = graphData.nodes.find(n => n.id === nodeId);
        if (targetNode) {
          const x = targetNode.x ?? 0;
          const y = targetNode.y ?? 0;
          const z = targetNode.z ?? 0;
          graphInstance.current.cameraPosition(
            { x, y, z: z + 100 },
            { x, y, z },
            1000
          );
          setSelectedNode(targetNode);
        }
      }
    }

    if (isLoading) {
      return <div>Loading...</div>;
    }

    const updateConnectedNodes = (node: Node) => {
      if (!graphData) return;
  
      const connected: { [groupId: string]: Node[] } = {};
      graphData.links.forEach(link => {
        if (link.source === node.id || link.target === node.id) {
          const connectedNodeId = link.source === node.id ? link.target : link.source;
          const connectedNode = graphData.nodes.find(n => n.id === connectedNodeId);
          if (connectedNode && connectedNode.group_id) {
            if (!connected[connectedNode.group_id]) {
              connected[connectedNode.group_id] = [];
            }
            connected[connectedNode.group_id].push(connectedNode);
          }
        }
      });
    };

    const handleConnectedNodeClick = (nodeId: number) => {
      const clickedNode = graphData?.nodes.find(n => n.id === nodeId);
      if (clickedNode) {
        setSelectedNode(clickedNode);
        updateConnectedNodes(clickedNode);
        // Center camera on clicked node
        if (graphInstance.current) {
          const x = clickedNode.x ?? 0;
          const y = clickedNode.y ?? 0;
          const z = clickedNode.z ?? 0;
          graphInstance.current.cameraPosition(
            { x, y, z: z + 100 },
            { x, y, z },
            1000
          );
        }
      }
    };
  
    if (!graphData) {
      return <div>No data available. Please try again later.</div>;
    }
  
    return (
      <div style={{ position: 'relative', width: '100vw', height: '90vh' }}>
        <div ref={graphRef} style={{ width: '100vw', height: '90vh' }} />
        {isPanelOpen && selectedNode && (
          <div ref={panelRef} style={{
            ...panelStyles,
            position: 'absolute',
            right: '20px',
            top: '20px',
          }}>
          <button onClick={() => setIsPanelOpen(false)} style={closeButtonStyles}>x</button>
          <div style={panelContentStyles}>
            {selectedNode.profile_picture && (
              <img 
                src={selectedNode.profile_picture} 
                alt={selectedNode.individual_name || selectedNode.username}
                style={profilePictureStyles}
              />
            )}
            <div>
            <h2>{selectedNode.individual_name || selectedNode.username}</h2>
              {selectedNode.username && selectedNode.username !== selectedNode.individual_name && (
                <p><strong>Username:</strong> {selectedNode.username}</p>
              )}
              {selectedNode.email && (
                <p><strong>Email:</strong> {selectedNode.email}</p>
              )}
              {selectedNode.header && (
                <p><strong>Header:</strong> {selectedNode.header}</p>
              )}
              {selectedNode.connection_order !== undefined && (
                <p><strong>Degree of Connection:</strong> {selectedNode.connection_order}</p>
              )}
              {selectedNode.group_id && (
                <p><strong>Group:</strong> {graphData?.groups.find(g => g.id === selectedNode.group_id)?.name}</p>
              )}
              {selectedNode.link && (
                <a href={selectedNode.link} target="_blank" rel="noopener noreferrer" style={linkStyles}>
                  Visit Profile
                </a>
              )}
            </div>
          </div>
          {selectedNode.corresponding_user_nodes.length > 0 && (
            <>
              <h3 style={{ fontSize: '16px', marginBottom: '10px' }}>Corresponding Nodes:</h3>
              <div style={correspondingNodesContainerStyles}>
              {selectedNode.corresponding_user_nodes.map(nodeId => {
                const correspondingNode = graphData.nodes.find(n => n.id === nodeId);
                if (correspondingNode) {
                  return (
                    <button
                      key={nodeId}
                      onClick={() => handleCorrespondingNodeClick(nodeId)}
                      style={correspondingNodeButtonStyles}
                    >
                      {correspondingNode.profile_picture && (
                        <img 
                          src={correspondingNode.profile_picture} 
                          alt={correspondingNode.individual_name || correspondingNode.username}
                          style={correspondingNodePictureStyles}
                        />
                      )}
                      <span style={correspondingNodeTextStyles}>
                      {correspondingNode.group_id && (
                        <span style={groupNameStyles}>
                          {graphData.groups.find(g => g.id === correspondingNode.group_id)?.name || 'Unknown Group'}
                        </span>
                      )}
                      </span>
                    </button>
                  );
                }
                return null;
              })}
              </div>
            </>
          )}
          </div>
        )}
      </div>
    );  
};

const panelStyles: React.CSSProperties = {
  width: '500px',
  backgroundColor: 'rgba(0, 0, 0, 0.6)', // More transparent background
  color: 'white',
  padding: '15px',
  borderRadius: '8px',
  overflowY: 'auto',
  maxHeight: '500px',
  marginTop: '70px',
  zIndex: 10,
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
};

const panelContentStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  marginBottom: '15px',
  paddingBottom: '15px',
};

const correspondingNodeTextStyles: React.CSSProperties = {
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
};

const groupNameStyles: React.CSSProperties = {
  fontSize: '10px',
  color: '#aaa',
  fontStyle: 'italic',
};


const profilePictureStyles: React.CSSProperties = {
  width: '60px',
  height: '60px',
  borderRadius: '50%',
  marginRight: '15px',
  objectFit: 'cover',
};


const correspondingNodeButtonStyles: React.CSSProperties = {
  background: 'transparent',
  border: '1px solid white',
  color: '#fff',
  padding: '5px 10px',
  cursor: 'pointer',
  borderRadius: '5px',
  display: 'flex',
  alignItems: 'center',
  fontSize: '12px',
};

const correspondingNodesContainerStyles: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '10px', 
  maxWidth: '100%', 
};


const caretStyles: React.CSSProperties = {
  position: 'absolute',
  bottom: '-10px',
  left: '50%',
  transform: 'translateX(-50%)',
  width: 0,
  height: 0,
  borderLeft: '10px solid transparent',
  borderRight: '10px solid transparent',
  borderTop: '10px solid rgba(0, 0, 0, 0.8)',
};

const linkStyles: React.CSSProperties = {
  color: '#4a90e2',
  textDecoration: 'none',
};

const correspondingNodePictureStyles: React.CSSProperties = {
  width: '20px',
  height: '20px',
  borderRadius: '50%',
  marginRight: '5px',
  objectFit: 'cover',
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
export default NetworkGraph;
