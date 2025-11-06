import React, { useEffect, useRef } from 'react'
import cytoscape from 'cytoscape'
import coseBilkent from 'cytoscape-cose-bilkent'

cytoscape.use(coseBilkent)

export default function GraphView({ graph, onNodeSelect }) {
  const ref = useRef(null)
  const cyRef = useRef(null)

  useEffect(() => {
    if (!ref.current) return
    if (!cyRef.current) {
      cyRef.current = cytoscape({
        container: ref.current,
        elements: [],
        style: [
          { selector: 'node', style: { 'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'width': 'mapData(degree, 0, 20, 20, 60)', 'height': 'mapData(degree, 0, 20, 20, 60)' } },
          { selector: 'edge', style: { 'width': 2, 'curve-style': 'bezier', 'target-arrow-shape': 'triangle' } },
          { selector: '.faded', style: { 'opacity': 0.2 } }
        ],
        layout: { name: 'cose-bilkent' }
      })

      cyRef.current.on('tap', 'node', (evt) => {
        const nd = evt.target.data()
        onNodeSelect(nd)
      })
    }

    const cy = cyRef.current
    if (graph) {
      const elements = []
      graph.nodes.forEach(n => {
        elements.push({ data: { id: n.id, label: n.label, degree: n.degree || 1, depth: n.depth || 0 } })
      })
      graph.edges.forEach(e => elements.push({ data: { id: `${e.from}->${e.to}`, source: e.from, target: e.to } }))

      cy.json({ elements })
      const layout = cy.layout({ name: 'cose-bilkent', animate: true })
      layout.run()
    }
  }, [graph, onNodeSelect])

  return <div ref={ref} style={{ width: '100%', height: '100%' }} />
}
