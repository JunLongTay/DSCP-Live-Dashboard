console.log("📦 Server file started");

const express = require('express');
const cors = require('cors');
const compression = require('compression');
const { Pool } = require('pg');

const app = express();
app.use(cors());
app.use(compression());

const pool = new Pool({
  user: 'npds_2025',
  host: 'db.tinkerthings.global',
  database: 'sensor_data',
  password: 'npds_2025_eh0atNiA5MVx2FYY3UnqVo5Vzv_0N9MRnSZ_3dkJgT_r2EIONEpFzV1o3IXHSFsjUX8hXT-9OgKqt8f512RPWJohKdM_pA-dAfimfXXOuke5C0Z9irOt4GrEV5R',
  port: 6970,
});

// Simple in-memory cache (expires in 30s)
const cache = new Map();
function getCached(key, ttl = 30000) {
  const item = cache.get(key);
  if (item && Date.now() - item.timestamp < ttl) return item.data;
  return null;
}
function setCache(key, data) {
  cache.set(key, { data, timestamp: Date.now() });
}

// Utility: Get limit from query or default
function getLimit(req, fallback = 100) {
  return Math.min(parseInt(req.query.limit) || fallback, 1000); // cap at 1000
}

// 1) Compost NPK
app.get('/compost-npk', async (req, res) => {
  const limit = getLimit(req);
  const cacheKey = `/compost-npk-${limit}`;
  const cached = getCached(cacheKey);
  if (cached) return res.json(cached);

  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        MAX(CASE WHEN s.sensor = 'Soil Nitrogen'   THEN sd.value::float END) AS nitrogen,
        MAX(CASE WHEN s.sensor = 'Soil Phosphorus' THEN sd.value::float END) AS phosphorus,
        MAX(CASE WHEN s.sensor = 'Soil Potassium'  THEN sd.value::float END) AS potassium
      FROM devicedata dd
      JOIN sensordata sd  ON sd.devicedataid = dd.devicedataid
      JOIN sensors s      ON sd.sensorid     = s.sensorid
      WHERE s.sensor IN ('Soil Nitrogen', 'Soil Phosphorus', 'Soil Potassium')
      GROUP BY dd.devicetimestamp
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);
    setCache(cacheKey, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /compost-npk failed:', err);
    res.status(500).send(err.message);
  }
});

// 2) Soil Temperature & CO₂
app.get('/soil-temp-co2', async (req, res) => {
  const limit = getLimit(req);
  const cacheKey = `/soil-temp-co2-${limit}`;
  const cached = getCached(cacheKey);
  if (cached) return res.json(cached);

  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        MAX(CASE WHEN s.sensor = 'Soil Temperature' THEN sd.value::float END) AS soil_temp,
        MAX(CASE WHEN s.sensor = 'CO2'              THEN sd.value::float END) AS co2
      FROM devicedata dd
      JOIN sensordata sd  ON sd.devicedataid = dd.devicedataid
      JOIN sensors s      ON sd.sensorid     = s.sensorid
      WHERE s.sensor IN ('Soil Temperature', 'CO2')
      GROUP BY dd.devicetimestamp
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);
    setCache(cacheKey, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /soil-temp-co2 failed:', err);
    res.status(500).send(err.message);
  }
});

// 3) All raw sensor data (debug only)
app.get('/all-sensor-data', async (req, res) => {
  const limit = getLimit(req, 100);
  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        s.sensor,
        sd.value::float AS value
      FROM devicedata dd
      JOIN sensordata sd  ON sd.devicedataid = dd.devicedataid
      JOIN sensors s      ON sd.sensorid     = s.sensorid
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);
    res.json(rows);
  } catch (err) {
    console.error('❌ /all-sensor-data failed:', err);
    res.status(500).send(err.message);
  }
});

// 4) Static Moisture Forecast
app.get('/moisture-forecast', (req, res) => {
  res.json([
    { timestamp: '2025-07-07T13:00:00Z', moisture: 31 },
    { timestamp: '2025-07-07T14:00:00Z', moisture: 30 },
    { timestamp: '2025-07-07T15:00:00Z', moisture: 29 }
  ]);
});

// 5) Soil Temperature by Device
app.get('/soil-temp-by-device', async (req, res) => {
  const limit = getLimit(req);
  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        d.devicename,
        MAX(CASE WHEN s.sensorid = 8 THEN sd.value::float END) AS soil_temp
      FROM sensordata sd
      JOIN devicedata dd
        ON sd.devicedataid = dd.devicedataid
        AND sd.parentdevicedbtimestamp = dd.dbtimestamp
      JOIN devices d ON dd.deviceid = d.deviceid
      JOIN sensors s ON sd.sensorid = s.sensorid
      WHERE d.deviceid IN (48, 49, 50, 51, 52, 53, 54, 55)
      GROUP BY dd.devicetimestamp, d.devicename
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);
    res.json(rows);
  } catch (err) {
    console.error('❌ /soil-temp-by-device failed:', err);
    res.status(500).send(err.message);
  }
});

// 6) Air Temperature from Device 56
app.get('/air-temp', async (req, res) => {
  const limit = getLimit(req);
  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        d.devicename,
        MAX(CASE WHEN s.sensorid = 2 THEN sd.value::float END) AS air_temp
      FROM sensordata sd
      JOIN devicedata dd
        ON sd.devicedataid = dd.devicedataid
        AND sd.parentdevicedbtimestamp = dd.dbtimestamp
      JOIN devices d ON dd.deviceid = d.deviceid
      JOIN sensors s ON sd.sensorid = s.sensorid
      WHERE d.deviceid IN (56)
      GROUP BY dd.devicetimestamp, d.devicename
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);
    res.json(rows);
  } catch (err) {
    console.error('❌ /air-temp failed:', err);
    res.status(500).send(err.message);
  }
});

// 7) Get ALL soil moisture data (limited for performance)
app.get('/moisture-all', async (req, res) => {
  const limit = getLimit(req, 200); // Default to 200 rows, adjustable with ?limit=
  const cacheKey = `/moisture-all-${limit}`;
  const cached = getCached(cacheKey);
  if (cached) return res.json(cached);

  try {
    const { rows } = await pool.query(`
      SELECT
        dd.devicetimestamp AS timestamp,
        d.devicename,
        sd.value::float AS moisture
      FROM devicedata dd
      JOIN sensordata sd ON sd.devicedataid = dd.devicedataid
      JOIN sensors s ON sd.sensorid = s.sensorid
      JOIN devices d ON dd.deviceid = d.deviceid
      WHERE s.sensor = 'Soil Moisture'
      ORDER BY dd.devicetimestamp DESC
      LIMIT $1
    `, [limit]);

    setCache(cacheKey, rows);
    res.json(rows);
  } catch (err) {
    console.error('❌ /moisture-all failed:', err);
    res.status(500).send(err.message);
  }
});



app.get('/table-samples', async (req, res) => {
  try {
    const tablesResult = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
    `);

    const previews = [];

    for (const row of tablesResult.rows) {
      const tableName = row.table_name;

      try {
        const dataResult = await pool.query(`SELECT * FROM "${tableName}" LIMIT 5`);
        if (dataResult.rows.length > 0) {
          previews.push({ table: tableName, rows: dataResult.rows });
        }
      } catch (err) {
        console.warn(`⚠️ Skipping ${tableName}:`, err.message);
      }
    }

    res.json(previews);
  } catch (err) {
    console.error('❌ /table-samples failed:', err);
    res.status(500).send(err.message);
  }
});

// Start server
app.listen(3001, () => console.log('✅ Backend running at http://localhost:3001'));
