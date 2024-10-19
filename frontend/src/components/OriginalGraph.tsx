import React from 'react';

const OriginalGraph = () => {
    const htmlContent = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Example Network Graph</title>
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                }

                #3d-graph {
                    width: 100%;
                    height: 100%;
                    position: absolute;
                    top: 0;
                    left: 0;
                }

                /* Modal styling */
                #node-modal {
                    display: none;
                    position: fixed;
                    top: 10%;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 60%; /* Increased modal width */
                    background: rgba(0, 0, 0, 0.8);
                    overflow: auto;
                    z-index: 1000;
                    padding: 20px;
                    box-sizing: border-box;
                    border-radius: 15px;
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    color: #fff;
                    text-align: left; /* Align all content to the left */
                }

                #node-modal button {
                    background: transparent;
                    border: none;
                    color: #fff; /* White close button */
                    font-size: 18px;
                    cursor: pointer;
                    position: absolute;
                    top: 10px;
                    right: 10px; /* Positioning the button in the top right */
                }

                #node-modal button:hover {
                    color: #aaa;
                }

                #modal-content h2 {
                    margin: 0;
                    font-weight: bold; /* Bolded name */
                }

                #modal-content h3 {
                    margin: 5px 0;
                }

                #modal-content p {
                    line-height: 1.5;
                }

                #modal-content img {
                    display: block;
                    margin-bottom: 20px;
                    border-radius: 50%;
                    width: 100px; /* Fixed image width */
                    height: 100px; /* Fixed image height */
                }
            </style>
        </head>
        <body>
            <div id="3d-graph"></div>
            <!-- Modal for node details -->
            <div id="node-modal">
                <button id="close-modal">Close</button>
                <div id="modal-content"></div>
            </div>

            <!-- Include Three.js and 3d-force-graph -->
            <script src="https://unpkg.com/three@0.154.0/build/three.min.js"></script>
            <script src="https://unpkg.com/3d-force-graph"></script>
            <script>
                // Fetch both the nodes and links JSON data
                Promise.all([
                fetch('/dummy_data/dummy_nodes.json').then(response => response.json()),
                fetch('/dummy_data/dummy_links.json').then(response => response.json())
                ])
                .then(([nodesData, linksData]) => {
                    // Combine nodes and links into a single graphData object
                    const graphData = {
                        nodes: nodesData,
                        links: linksData
                    };

                    // Index nodes by their id for quick access
                    const nodeById = Object.fromEntries(graphData.nodes.map(node => [node.id, node]));

                    // Variable to track the activated group
                    let activatedGroupName = null;

                    // Create the force graph with the combined data
                    const Graph = ForceGraph3D()
                        (document.getElementById('3d-graph'))
                        .graphData(graphData)
                        .backgroundColor('#000022')
                        .nodeAutoColorBy('group_name') // Color nodes by group
                        .linkWidth(2)
                        .nodeThreeObject(node => {
                            if (node.expanded) {
                                // Create a group to hold the sphere and labels
                                const nodeGroup = new THREE.Group();

                                // Create the node sphere
                                const sphereGeometry = new THREE.SphereGeometry(5);
                                const sphereMaterial = new THREE.MeshBasicMaterial({ color: node.color || 'lightblue' });
                                const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                                nodeGroup.add(sphere);

                                // Add profile picture with circular mask
                                const imgTexture = new THREE.TextureLoader().load(node.profile_picture);
                                const imgMaterial = new THREE.SpriteMaterial({ map: imgTexture });
                                const sprite = new THREE.Sprite(imgMaterial);
                                sprite.scale.set(10, 10, 1); // Adjust the size
                                sprite.position.set(-15, 10, 0); // Adjust position to top left
                                nodeGroup.add(sprite);

                                // Add text labels
                                const labelText = node.individual_name + "\n" + node.group_name + "\n" + node.summarized_description;
                                const label = createTextSprite(labelText, { fontsize: 24 }); // Larger font
                                label.position.set(15, -10, 0); // Adjust position to avoid overlap
                                nodeGroup.add(label);

                                return nodeGroup;
                            } else {
                                // By default, render nodes as simple spheres
                                const sphereGeometry = new THREE.SphereGeometry(5);
                                const sphereMaterial = new THREE.MeshBasicMaterial({ color: node.color || 'lightblue' });
                                const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                                return sphere;
                            }
                        })
                        .onNodeClick(node => {
                            if (activatedGroupName === null || activatedGroupName !== node.group_name) {
                                // Activate the group
                                activatedGroupName = node.group_name;

                                // Expand nodes in the group
                                expandGroupNodes(node.group_name);

                                // Optionally, zoom into the group
                                const groupNodeIds = getGroupNodeIds(node.group_name);
                                Graph.zoomToFit(1000, 50, n => groupNodeIds.includes(n.id));

                                // Refresh the graph to update the nodes
                                Graph.refresh();
                            } else {
                                // The group is already activated, show the modal popup
                                showNodeModal(node);
                            }
                        });

                    // Function to expand nodes in a group
                    function expandGroupNodes(groupName) {
                        graphData.nodes.forEach(node => {
                            node.expanded = node.group_name === groupName;
                        });
                    }

                    // Function to get all node IDs in the same group
                    function getGroupNodeIds(groupName) {
                        return graphData.nodes
                            .filter(n => n.group_name === groupName)
                            .map(n => n.id);
                    }

                    // Handle background clicks
                    Graph.onBackgroundClick(event => {
                        // Deactivate the group
                        activatedGroupName = null;

                        // Collapse all expanded nodes
                        graphData.nodes.forEach(node => {
                            node.expanded = false;
                        });

                        // Refresh the graph
                        Graph.refresh();
                    });

                    // Function to create text sprite
                    function createTextSprite(message, parameters) {
                        if (parameters === undefined) parameters = {};

                        const fontface = parameters.fontface || 'Arial';
                        const fontsize = parameters.fontsize || 18;
                        const borderThickness = parameters.borderThickness || 4;
                        const backgroundColor = parameters.backgroundColor || { r:255, g:255, b:255, a:0.0 };
                        const textColor = parameters.textColor || { r: 255, g: 255, b: 255, a: 1.0 };

                        const canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');

                        context.font = fontsize + "px " + fontface;

                        // Get size data (height depends only on font size)
                        const lines = message.split('\n');
                        const lineHeight = fontsize * 1.4;
                        const textWidth = Math.max(...lines.map(line => context.measureText(line).width));

                        canvas.width = textWidth + borderThickness * 2;
                        canvas.height = lineHeight * lines.length + borderThickness * 2;

                        // Make sure the context uses the correct size
                        context.font = fontsize + "px " + fontface;
                        context.textBaseline = 'top';

                        // Draw text
                        lines.forEach((line, index) => {
                            // Bold the first line (name)
                            if (index === 0) {
                                context.font = "Bold " + fontsize + "px " + fontface;
                            } else {
                                context.font = fontsize + "px " + fontface;
                            }
                            context.fillStyle = 'rgba(' + textColor.r + ',' + textColor.g + ',' + textColor.b + ',' + textColor.a + ')';
                            context.fillText(line, borderThickness, borderThickness + lineHeight * index);
                        });

                        // Canvas contents will be used for a texture
                        const texture = new THREE.CanvasTexture(canvas);
                        texture.minFilter = THREE.LinearFilter;
                        texture.needsUpdate = true;
                        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
                        const sprite = new THREE.Sprite(spriteMaterial);
                        sprite.scale.set(canvas.width / 15, canvas.height / 15, 1.0); // Adjust the scale as needed

                        return sprite;

                    }

                    // Function to show node modal
                    function showNodeModal(node) {
                        const modalContent = document.getElementById('modal-content');
                        modalContent.innerHTML = 
                            '<div style="display: flex; align-items: flex-start;">' +
                                '<img src="' + node.profile_picture + '" style="width:100px; height:100px; border-radius:50%; margin-right:20px;" />' +
                                '<div>' +
                                    '<h2>' + node.individual_name + '</h2>' +
                                    '<h3>' + node.group_name + '</h3>' +
                                    '<p>' + node.comprehensive_description + '</p>' +
                                    '<p>Email: <a href="mailto:' + node.email + '" style="color: #fff;">' + node.email + '</a></p>' +
                                    '<p>Connection Order: ' + node.connection_order + '</p>' +
                                    '<p><a href="' + node.link + '" target="_blank" style="color: #fff;">Visit Profile</a></p>' +
                                '</div>' +
                            '</div>' +
                            (node.corresponding_node 
                                ? '<div style="position: absolute; bottom: 100px; left: 100px;"><button id="focus-node-btn" style="color: #fff; background: none; border: none; cursor: pointer;">See other profile</button></div>' 
                                : '');

                        if (node.corresponding_node) {
                            document.getElementById('focus-node-btn').addEventListener('click', () => {
                                const targetNode = graphData.nodes.find(n => n.id === node.corresponding_node);
                                if (targetNode) {
                                    // Deactivate the current group
                                    activatedGroupName = null;
                                    graphData.nodes.forEach(n => {
                                        n.expanded = false;
                                    });

                                    // Activate the group of the target node
                                    activatedGroupName = targetNode.group_name;
                                    expandGroupNodes(targetNode.group_name);

                                    // Refresh the graph
                                    Graph.refresh();

                                    // Move the camera to the target node
                                    Graph.cameraPosition(
                                        { x: targetNode.x, y: targetNode.y, z: targetNode.z + 100 },
                                        targetNode,
                                        3000 // ms transition duration
                                    );
                                    document.getElementById('node-modal').style.display = 'none';
                                }
                            });
                        }

                        // Show the modal
                        document.getElementById('node-modal').style.display = 'block';
                    }

                    // Event listener to close the modal
                    document.getElementById('close-modal').addEventListener('click', () => {
                        document.getElementById('node-modal').style.display = 'none';
                    });
                })
                .catch(error => {
                    console.error('Error loading the JSON files:', error);
                });
            </script>
        </body>
    </html>
    `
    return (
        <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
    );
};

export default OriginalGraph;