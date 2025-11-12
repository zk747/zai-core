import React, { useEffect, useState } from "react";

export default function App() {
  const [nodeStatus, setNodeStatus] = useState("⏳ Checking...");
  const [aiStatus, setAiStatus] = useState("⏳ Checking...");

  useEffect(() => {
    async function checkServices() {
      try {
        const node = await fetch("http://localhost:4000/ping");
        if (node.ok) setNodeStatus("✅ Online");
        else setNodeStatus("❌ Offline");
      } catch {
        setNodeStatus("❌ Offline");
      }

      try {
        const ai = await fetch("http://localhost:8000/ping");
        if (ai.ok) setAiStatus("✅ Online");
        else setAiStatus("❌ Offline");
      } catch {
        setAiStatus("❌ Offline");
      }
    }

    checkServices();
    const interval = setInterval(checkServices, 5000); // check every 5s
    return () => clearInterval(interval);
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
