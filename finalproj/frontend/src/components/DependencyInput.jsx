import React, { useState } from 'react';

export default function DependencyInput({ onGraph }) {
  const [status, setStatus] = useState('');

  const handleFile = async e => {
    const file = e.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    setStatus('Uploading...');
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    const data = await res.json();
    onGraph(data);
    setStatus('Loaded.');
  };

  const handlePaste = async e => {
    e.preventDefault();
    const text = e.clipboardData.getData('text');
    try {
      const blob = new Blob([text], { type: 'application/json' });
      const form = new FormData();
      form.append('file', blob, 'paste.json');
      const res = await fetch('/api/upload', { method: 'POST', body: form });
      const data = await res.json();
      onGraph(data);
    } catch {
      alert('Invalid JSON.');
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <label>
        Load dependency JSON: <input type="file" accept=".json" onChange={handleFile} />
      </label>
      <div
        onPaste={handlePaste}
        style={{
          border: '1px dashed #888',
          marginTop: '0.5rem',
          padding: '1rem',
          minHeight: '80px',
          cursor: 'text'
        }}
      >
        Paste JSON here (Ctrl+V)
      </div>
      <p>{status}</p>
    </div>
  );
}
