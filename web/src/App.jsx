import React, { useState, useEffect } from 'react';

const AGENTS = [
  'CodeArchitect',
  'IdeasAgent',
  'CreativityAgent',
  'QCChecker',
  'TestHarnessAgent',
  'SelfScoringAgent',
];

function App() {
  const [agent, setAgent] = useState(AGENTS[0]);
  const [params, setParams] = useState('{}');
  const [taskId, setTaskId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const submit = async () => {
    setStatus('pending');
    setResult(null);
    const res = await fetch('/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent, params: JSON.parse(params) }),
    });
    const data = await res.json();
    setTaskId(data.id);
  };

  useEffect(() => {
    if (!taskId) return;
    const iv = setInterval(async () => {
      const res = await fetch(`/tasks/${taskId}`);
      const d = await res.json();
      setStatus(d.status);
      if (d.status === 'SUCCESS' || d.status === 'FAILURE') {
        setResult(d.result);
        clearInterval(iv);
      }
    }, 1500);
    return () => clearInterval(iv);
  }, [taskId]);

  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>THE AGENCY Dashboard</h1>
      <div>
        <label>Agent: </label>
        <select value={agent} onChange={e => setAgent(e.target.value)}>
          {AGENTS.map(a => <option key={a}>{a}</option>)}
        </select>
      </div>
      <div style={{ marginTop: 10 }}>
        <label>Params (JSON): </label>
        <textarea
          rows={4}
          cols={60}
          value={params}
          onChange={e => setParams(e.target.value)}
        />
      </div>
      <button onClick={submit} style={{ marginTop: 10 }}>Submit Task</button>
      {taskId && (
        <div style={{ marginTop: 20 }}>
          <strong>Task ID:</strong> {taskId}<br/>
          <strong>Status:</strong> {status}<br/>
          {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
        </div>
      )}
      {/* Task history */}
      <div style={{ marginTop: 40 }}>
        <h2>Task History</h2>
        <button onClick={async () => {
          const res = await fetch('/tasks_all');
          const data = await res.json();
          setHistory(Object.values(data));
        }}>Refresh History</button>
        <table border={1} cellPadding={5} style={{ marginTop: 10 }}>
          <thead><tr><th>ID</th><th>Agent</th><th>Status</th><th>Result</th></tr></thead>
          <tbody>
            {history.map(h => (
              <tr key={h.id}>
                <td>{h.id}</td>
                <td>{h.agent}</td>
                <td>{h.status}</td>
                <td><pre style={{ maxHeight: 100, overflow: 'auto' }}>{JSON.stringify(h.result, null, 2)}</pre></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
