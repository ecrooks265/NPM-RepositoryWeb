import React from 'react'

export default function NodePanel({ node }) {
  if (!node) return <div className="nodepanel">Click a node to see details</div>
  return (
    <div className="nodepanel">
      <h2>{node.label}</h2>
      <p><strong>id:</strong> {node.id}</p>
      {node.depth !== undefined && <p><strong>depth:</strong> {node.depth}</p>}
      {node.degree !== undefined && <p><strong>direct deps:</strong> {node.degree}</p>}
      {node.error && <p className="error">Error: {node.error}</p>}
      <p><em>Click another node to inspect it.</em></p>
    </div>
  )
}
