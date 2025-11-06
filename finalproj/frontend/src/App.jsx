import React, { useState } from 'react'
import GraphView from './components/GraphView'
import NodePanel from './components/NodePanel'

export default function App() {
  const [graph, setGraph] = useState(null)
  const [selectedNode, setSelectedNode] = useState(null)
  const [loading, setLoading] = useState(false)

  async function fetchGraph(pkgName, depth=2) {
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/dependencies/${encodeURIComponent(pkgName)}?depth=${depth}`)
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setGraph(data)
    } catch (e) {
      alert('Error fetching graph: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>NPM Dependency Web</h1>
        <div className="controls">
          <input id="pkg-input" placeholder="Enter an npm package (e.g. express)" />
          <button onClick={() => {
            const v = document.getElementById('pkg-input').value.trim()
            if (v) fetchGraph(v, 2)
          }} disabled={loading}>Fetch</button>
        </div>
      </header>

      <main className="main">
        <section className="graph">
          <GraphView graph={graph} onNodeSelect={setSelectedNode} />
        </section>
        <aside className="panel">
          <NodePanel node={selectedNode} />
        </aside>
      </main>

      <footer className="footer">Local demo • npm registry</footer>
    </div>
  )
}
