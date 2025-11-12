import { useEffect, useState } from "react";

export default function App() {
  const [nodeStatus, setNodeStatus] = useState("⏳ Checking…");
  const [aiStatus, setAiStatus] = useState("⏳ Checking…");

  useEffect(() => {
    fetch("http://localhost:4000")
      .then(() => setNodeStatus("✅ Online"))
      .catch(() => setNodeStatus("❌ Offline"));

    fetch("http://localhost:8000")
      .then(() => setAiStatus("✅ Online"))
      .catch(() => setAiStatus("❌ Offline"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: 40 }}>
      <h1>ZAI Dashboard ⚡</h1>
      <p>Your local ZAI Core is running.</p>

      <h2>Service Status</h2>
      <ul>
        <li>Node API (4000): {nodeStatus}</li>
        <li>Python AI (8000): {aiStatus}</li>
      </ul>
    </div>
  );
}
