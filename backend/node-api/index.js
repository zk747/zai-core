import express from "express";
import pkg from "pg";
import Redis from "ioredis";

const { Pool } = pkg;
const app = express();
const port = process.env.PORT || 4000;

const pool = new Pool({
  connectionString: process.env.DB_URL,
});

const redis = new Redis({ host: process.env.REDIS_HOST || "redis" });

app.get("/", (req, res) => res.send("ZAI Node API running ✅"));

app.get("/health", async (req, res) => {
  try {
    const now = await pool.query("SELECT NOW()");
    const ping = await redis.ping();
    res.json({ db: now.rows[0], redis: ping });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => console.log(`Node API listening on ${port}`));
