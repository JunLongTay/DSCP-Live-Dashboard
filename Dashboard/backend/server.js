require('dotenv').config();
console.log('🔐 ENV Loaded:', {
  PG_HOST: process.env.PG_HOST,
  PG_PORT: process.env.PG_PORT,
  PG_USER: process.env.PG_USER,
});

const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));
const express = require('express');
const cors = require('cors');
const compression = require('compression');
const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

console.log("📦 Fully Optimized Server Starting...");

const app = express();
app.use(cors());
app.use(compression());

// 🛠️ Connection Pool with Enhanced Settings
const pool = new Pool({
  user: process.env.PG_USER,
  host: process.env.PG_HOST,
  database: process.env.PG_DATABASE,
  password: process.env.PG_PASSWORD,
  port: parseInt(process.env.PG_PORT, 10),
  max: 20,
  idleTimeoutMillis: 30000, 
  connectionTimeoutMillis: 10000,
  maxUses: 7500,
  statement_timeout: 600000,
  query_timeout: 600000,
});

// 🚀 Enhanced In-Memory Cache
const CACHE_MAX_SIZE = 1000;
const CACHE_DEFAULT_TTL = 30000;
const cache = new Map();

function getCached(key, ttl = CACHE_DEFAULT_TTL) {
  const item = cache.get(key);
  if (item && Date.now() - item.timestamp < ttl) return item.data;
  return null;
}

function setCache(key, data) {
  if (cache.size >= CACHE_MAX_SIZE) {
    const oldestKey = cache.keys().next().value;
    cache.delete(oldestKey);
  }
  cache.set(key, { data, timestamp: Date.now() });
}

// 🧠 SQL Loader
function loadQueries(filepath) {
  const content = fs.readFileSync(filepath, 'utf8');
  const queryMap = {};
  const blocks = content.split('-- name: ').slice(1);
  for (const block of blocks) {
    const [nameLine, ...queryLines] = block.split('\n');
    const name = nameLine.trim();
    const query = queryLines.join('\n').trim();
    queryMap[name] = query;
  }
  return queryMap;
}

const queries = loadQueries(path.join(__dirname, 'queries.sql'));

// 🔄 Helpers
function getLimit(req, fallback = 100) {
  return Math.min(parseInt(req.query.limit) || fallback, 1000);
}

// 📊 Endpoints
app.get('/compost-npk', async (req, res) => {
  const key = 'compost-npk-' + getLimit(req);
  const cached = getCached(key);
  if (cached) return res.json(cached);
  try {
    const { rows } = await pool.query(queries['compost-npk'], [getLimit(req)]);
    setCache(key, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /compost-npk failed:', err);
    res.status(500).send(err.message);
  }
});

app.get('/soil-temp-co2', async (req, res) => {
  const key = 'soil-temp-co2-' + getLimit(req);
  const cached = getCached(key);
  if (cached) return res.json(cached);
  try {
    const { rows } = await pool.query(queries['soil-temp-co2'], [getLimit(req)]);
    setCache(key, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /soil-temp-co2 failed:', err);
    res.status(500).send(err.message);
  }
});

app.get('/moisture-all', async (req, res) => {
  const bucketMin = Math.max(parseInt(req.query.bucket_min) || 2, 1);
  const windowMin = Math.max(parseInt(req.query.window_min) || 120, bucketMin);
  const key = `moisture-all-${bucketMin}-${windowMin}`;
  const cached = getCached(key);
  if (cached) return res.json(cached);
  try {
    const { rows } = await pool.query(queries['moisture-all'], [bucketMin, windowMin]);
    setCache(key, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /moisture-all failed:', err);
    res.status(500).send(err.message);
  }
});

app.get('/device-names', async (req, res) => {
  try {
    const { rows } = await pool.query(queries['device-names']);
    const names = rows.map(r => r.devicename);
    res.json(names);
  } catch (err) {
    console.error('❌ /device-names failed:', err);
    res.status(500).send(err.message);
  }
});

app.get('/health', (req, res) => {
  res.json({
    uptime: process.uptime(),
    cacheSize: cache.size,
    connections: pool.totalCount,
    idleConnections: pool.idleCount,
    waitingRequests: pool.waitingCount,
  });
});

async function warmUpCache() {
  const endpoints = [
    'moisture-all?bucket_min=5&window_min=30',
    'compost-npk?limit=1',
    'soil-temp-co2?limit=1',
  ];
  for (const route of endpoints) {
    const url = `http://localhost:3001/${route}`;
    console.log(`⏳ Warming cache from ${url}`);
    try {
      await new Promise(r => setTimeout(r, 500));
      const res = await fetch(url);
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      console.log(`🔥 Warmed ${route}: ${data.length} rows`);
    } catch (err) {
      console.error(`❌ Failed for ${route}: ${err.message}`);
    }
  }
}

app.listen(3001, () => {
  console.log('✅ Fully Optimized backend running at http://localhost:3001');
  warmUpCache();
});
