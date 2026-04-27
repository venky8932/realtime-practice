const express = require("express");
const axios = require("axios");

const app = express();
const PORT = parseInt(process.env.PORT, 10) || 3000;
const FASTAPI_URL = process.env.FASTAPI_URL || "http://fastapi-service:8000";
const CHECK_INTERVAL_MS = 300000;

app.use(express.json());

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

app.get("/fetch-users", async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_URL}/users`, { timeout: 10000 });
    res.json(response.data);
  } catch (error) {
    res.status(502).json({ error: error.message });
  }
});

app.get("/ping-fastapi", async (req, res) => {
  try {
    const response = await axios.get(`${FASTAPI_URL}/health`, { timeout: 10000 });
    res.json({ fastapi: response.data, status: response.status });
  } catch (error) {
    res.status(502).json({ error: error.message });
  }
});

// Self-health scheduler checks the local /health endpoint every 5 minutes.
// If the internal health check fails, the process exits so Kubernetes can restart the pod.
setInterval(async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:${PORT}/health`, { timeout: 5000 });
    if (res.status !== 200) throw new Error("Health check failed");
    console.log("[nodejs] self health passed");
  } catch (error) {
    console.error("[nodejs] self health failed", error.message || error);
    process.exit(1);
  }
}, CHECK_INTERVAL_MS);

app.listen(PORT, () => {
  console.log(`Node.js service running on port ${PORT}`);
});
