import React from 'react';

export default function SidePanel({ node }) {
  if (!node) {
    return (
      <aside
        style={{
          width: '300px',
          background: '#f8f8f8',
          borderLeft: '1px solid #ddd',
          padding: '1rem',
          fontSize: '14px'
        }}
      >
        <p>Select a node to view details.</p>
      </aside>
    );
  }

  return (
    <aside
      style={{
        width: '300px',
        background: '#fafafa',
        borderLeft: '1px solid #ddd',
        padding: '1rem',
        overflowY: 'auto',
        fontSize: '14px'
      }}
    >
      <h2 style={{ fontSize: '16px', marginBottom: '0.5rem' }}>
        {node.id} <small style={{ color: '#666' }}>v{node.version || 'N/A'}</small>
      </h2>

      <p>
        <strong>Maintainers:</strong> {node.maintainer_count || 0}
      </p>
      {node.maintainers && node.maintainers.length > 0 && (
        <ul>
          {node.maintainers.map((m, i) => (
            <li key={i}>{m}</li>
          ))}
        </ul>
      )}

      <p>
        <strong>Vulnerabilities:</strong> {node.vulnerability_count || 0}
      </p>
      {node.vulnerabilities && node.vulnerabilities.length > 0 && (
        <ul>
          {node.vulnerabilities.map((v, i) => (
            <li key={i}>
              <b>{v.id}</b> – {v.summary}
            </li>
          ))}
        </ul>
      )}

      <p>
        <strong>Connected Packages:</strong>
      </p>
      <ul>
        {node.connectedNodes.map((n, i) => (
          <li key={i}>{n}</li>
        ))}
      </ul>
    </aside>
  );
}
