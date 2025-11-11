import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import SidePanel from './SidePanel';

cytoscape.use(coseBilkent);

export default function GraphView({ graphData }) {
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (!graphData?.nodes?.length) return;

    // Destroy old instance if it exists
    if (cyRef.current) cyRef.current.destroy();

    // Filter valid edges
    const validEdges = (graphData.edges || []).filter(e => {
      const src = graphData.nodes.some(n => n.data.id === e.data.source);
      const tgt = graphData.nodes.some(n => n.data.id === e.data.target);
      return src && tgt;
    });

    cyRef.current = cytoscape({
      container: document.getElementById('cy'),
      elements: [...graphData.nodes, ...validEdges],
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(id)',
            'background-color': ele =>
              ele.data('vulnerability_count') > 0 ? '#E24A4A' : '#4B9CE2',
            'width': ele => 40 + (ele.data('maintainer_count') || 0) * 6,
            'height': ele => 40 + (ele.data('maintainer_count') || 0) * 6,
            'color': '#fff',
            'font-size': 12,
            'text-valign': 'center',
            'text-halign': 'center'
          }
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#ccc'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#FFD700'
          }
        }
      ],
      layout: { name: 'cose-bilkent', animate: false }
    });

    // Click listener for node
    cyRef.current.on('tap', 'node', evt => {
      const nodeData = evt.target.data();
      const connectedEdges = evt.target.connectedEdges().map(e => e.data());
      const connectedNodes = evt.target.connectedNodes().map(n => n.data().id);
      setSelectedNode({
        ...nodeData,
        connectedEdges,
        connectedNodes
      });
    });

    cyRef.current.on('tap', evt => {
      if (evt.target === cyRef.current) setSelectedNode(null);
    });

    return () => cyRef.current.destroy();
  }, [graphData]);

  return (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <div id="cy" style={{ flex: 1, height: '80vh', border: '1px solid #ccc' }} />
      <SidePanel node={selectedNode} />
    </div>
  );
}
