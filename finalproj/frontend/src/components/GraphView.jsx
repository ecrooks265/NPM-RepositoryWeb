import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import SidePanel from './SidePanel';

cytoscape.use(coseBilkent);

export default function GraphView({ graphData }) {
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [typosquats, setTyposquats] = useState([]);

  useEffect(() => {
    if (!graphData?.nodes?.length) return;

    // Destroy old instance
    if (cyRef.current) cyRef.current.destroy();

    // Validate edges to avoid broken refs
    const validEdges = (graphData.edges || []).filter(e => {
      const src = graphData.nodes.some(n => n.data.id === e.data.source);
      const tgt = graphData.nodes.some(n => n.data.id === e.data.target);
      return src && tgt;
    });

    // Init Cytoscape instance
    cyRef.current = cytoscape({
      container: document.getElementById('cy'),
      elements: [...graphData.nodes, ...validEdges],
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(id)',
            'text-outline-width': 0.75,
            'text-outline-color': '#0d0d1a',
            color: '#00ffff',
            'font-size': 10,
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': ele => {
              if (ele.data('vulnerability_count') > 0) return '#ff0055';
              if (ele.data('github')?.repo?.contributors?.length > 10)
                return '#00ffff';
              return '#7d2eff';
            },
            'width': ele => {
              const contribs = ele.data('github')?.repo?.contributors?.length || 1;
              return Math.min(100, 30 + Math.sqrt(contribs) * 6);
            },
            'height': ele => {
              const contribs = ele.data('github')?.repo?.contributors?.length || 1;
              return Math.min(100, 30 + Math.sqrt(contribs) * 6);
            },
            'border-width': 2,
          }
        },
        {
          selector: 'edge',
          style: {
            width: 1.8,
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            opacity: 0.8
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 2,
            'border-color': '#00ffff',
          }
        }
      ],
      layout: { name: 'cose-bilkent', animate: true, fit: true, padding: 50 }
    });

 // Fetch similar package names (typosquats)
  const fetchTyposquats = async (pkgName) => {
    try {
      const res = await fetch(`/api/typosquats/${pkgName}`);
      const data = await res.json();
      setTyposquats(data.similar_names || []);
    } catch (err) {
      console.error("Typosquatting fetch error:", err);
      setTyposquats([]);
    }
  };

  // Node click handler
  cyRef.current.on('tap', 'node', (evt) => {
    const nodeData = evt.target.data();
    const connectedEdges = evt.target.connectedEdges().map(e => e.data());
    const connectedNodes = evt.target.connectedNodes().map(n => n.data().id);

    setSelectedNode({
      ...nodeData,
      connectedEdges,
      connectedNodes
    });

    // Call fetchTyposquats here for the clicked node
    fetchTyposquats(nodeData.id);
  });

  // Background click clears selection
  cyRef.current.on('tap', (evt) => {
    if (evt.target === cyRef.current) {
      setSelectedNode(null);
      setTyposquats([]);
    }
  });

  return () => cyRef.current.destroy();
}, [graphData]);

  return (
    <div className="graph-container">
      <div id="cy" className="cytoscape-view" />
      <div className={`sidepanel-wrapper ${selectedNode ? 'open' : ''}`}>
        <SidePanel node={selectedNode} typosquats={typosquats}/>
      </div>
    </div>
  );
}
