function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: 40 }}>
      <h1>ZAI Dashboard ⚡</h1>
      <p>Your local ZAI Core is running.</p>
      <ul>
        <li><a href="http://localhost:4000" target="_blank">Node API (4000)</a></li>
        <li><a href="http://localhost:8000" target="_blank">Python AI (8000)</a></li>
        <li><a href="http://localhost:5601" target="_blank">Kibana (5601)</a></li>
      </ul>
    </div>
  );
}
export default App;
