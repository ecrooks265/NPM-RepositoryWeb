import React, { useState } from 'react';
import GraphView from './components/GraphView';
import DependencyInput from './components/DependencyInput';

export default function App() {
  const [pkgName, setPkgName] = useState('');
  const [graphData, setGraphData] = useState(null);

  async function fetchPackage() {
    const res = await fetch(`/api/dependencies/${pkgName}`);
    const data = await res.json();
    setGraphData(data);
  }

  return (
    <main style={{ padding: '1rem' }}>
      <h1>Dependency Intelligence Web</h1>

      <DependencyInput onGraph={setGraphData} />

      <div style={{ margin: '1rem 0' }}>
        <input
          placeholder="Search npm package (e.g. express)"
          value={pkgName}
          onChange={e => setPkgName(e.target.value)}
        />
        <button onClick={fetchPackage}>Fetch</button>
      </div>

      {graphData ? (
        <GraphView graphData={graphData} />
      ) : (
        <p>Upload JSON or search a package to visualize.</p>
      )}
    </main>
  );
}
  