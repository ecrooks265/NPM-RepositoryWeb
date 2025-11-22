import React from 'react';

export default function SidePanel({ node, typosquats = []  }) {
  if (!node) {
    return (
      <aside className="sidepanel empty">
        <p className="text-faint">Select a node to view details.</p>
      </aside>
    );
  }
  
  return (
    <aside className="sidepanel">
      <h2 className="neon-text">
        {node.id}
        <small className="version-tag">v{node.version || 'N/A'}</small>
      </h2>

      {typosquats.length > 0 && (
        <section className="panel-section">
          <h3>Potential Typosquatting Packages</h3>
          <ul className="data-list">
            {typosquats.map((pkg, i) => (
              <li key={i}>
                <b>{pkg.name}</b> 
                <span className="text-faint"> (score: {pkg.score})</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="panel-section">
        <h3>Maintainers</h3>
        <p>{node.maintainer_count || 0} maintainers</p>
        {node.maintainers && node.maintainers.length > 0 && (
          <ul className="data-list">
            {node.maintainers.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel-section">
        <h3>Vulnerabilities</h3>
        <p>{node.vulnerability_count || 0} known issues</p>
        {node.vulnerabilities && node.vulnerabilities.length > 0 && (
          <ul className="data-list">
            {node.vulnerabilities.map((v, i) => (
              <li key={i}>
                <b className="highlight">{v.id}</b> – {v.summary}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel-section">
        <h3>Connected Packages</h3>
        <ul className="data-list">
          {node.connectedNodes?.length > 0 ? (
            node.connectedNodes.map((n, i) => <li key={i}>{n}</li>)
          ) : (
            <li className="text-faint">No connections</li>
          )}
        </ul>
      </section>
    </aside>
  );
}
