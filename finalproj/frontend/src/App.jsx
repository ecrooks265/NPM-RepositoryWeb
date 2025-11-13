import React, { useState } from 'react';
import GraphView from './components/GraphView';
import DependencyInput from './components/DependencyInput';
import SidePanel from './components/SidePanel';

export default function App() {
  const [pkgName, setPkgName] = useState('');
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  async function fetchPackage() {
    if (!pkgName.trim()) return;
    const res = await fetch(`/api/dependencies/${pkgName}`);
    const data = await res.json();
    setGraphData(data);
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Graph Area */}
      <main className="flex-1 p-4">
        <h1 className="text-2xl font-bold mb-4">NPM Dependency Map</h1>

        <div className="mb-4 flex items-center gap-2">
          <input
            className="border border-gray-300 rounded px-2 py-1 w-64"
            placeholder="Search npm package (e.g. express)"
            value={pkgName}
            onChange={(e) => setPkgName(e.target.value)}
          />
          <button
            onClick={fetchPackage}
            className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
          >
            Fetch
          </button>
        </div>

        <DependencyInput onGraph={setGraphData} />

        {graphData ? (
          <GraphView
            graphData={graphData}
            onNodeClick={setSelectedNode}
          />
        ) : (
          <p className="text-gray-600">Upload JSON or search a package to visualize.</p>
        )}
      </main>

      {/* Sidebar */}
      {selectedNode && (
        <aside className="w-96 border-l border-gray-300 bg-white overflow-y-auto">
          <SidePanel pkg={selectedNode} onClose={() => setSelectedNode(null)} />
        </aside>
      )}
    </div>
  );
}
