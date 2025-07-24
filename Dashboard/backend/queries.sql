-- name: compost-npk
SELECT
  dd.devicetimestamp AS timestamp,
  MAX(CASE WHEN s.sensor = 'Soil Nitrogen' THEN sd.value::float END) AS nitrogen,
  MAX(CASE WHEN s.sensor = 'Soil Phosphorus' THEN sd.value::float END) AS phosphorus,
  MAX(CASE WHEN s.sensor = 'Soil Potassium' THEN sd.value::float END) AS potassium
FROM devicedata dd
JOIN sensordata sd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
WHERE s.sensor IN ('Soil Nitrogen', 'Soil Phosphorus', 'Soil Potassium')
  AND dd.devicetimestamp >= NOW() - interval '7 days'
GROUP BY dd.devicetimestamp
ORDER BY dd.devicetimestamp DESC
LIMIT $1;

-- name: soil-temp-co2
SELECT
  dd.devicetimestamp AS timestamp,
  MAX(CASE WHEN s.sensor = 'Soil Temperature' THEN sd.value::float END) AS soil_temp,
  MAX(CASE WHEN s.sensor = 'CO2' THEN sd.value::float END) AS co2
FROM devicedata dd
JOIN sensordata sd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
WHERE s.sensor IN ('Soil Temperature', 'CO2')
  AND dd.devicetimestamp >= NOW() - interval '7 days'
GROUP BY dd.devicetimestamp
ORDER BY dd.devicetimestamp DESC
LIMIT $1;

-- name: moisture-all
SELECT 
  to_timestamp(floor(extract('epoch' from dd.devicetimestamp) / ($1 * 60)) * ($1 * 60)) AT TIME ZONE 'UTC' AS timestamp,
  d.devicename,
  AVG(sd.value::float) AS moisture
FROM devicedata dd
JOIN sensordata sd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
JOIN devices d ON dd.deviceid = d.deviceid
WHERE s.sensor = 'Soil Moisture'
  AND dd.devicetimestamp >= NOW() - make_interval(mins := $2)
  AND d.devicename ILIKE 'NP Group%Plant Pot%'
GROUP BY timestamp, d.devicename
ORDER BY timestamp DESC;

-- name: device-names
SELECT devicename
FROM devices
WHERE devicename ILIKE 'NP Group%Plant Pot%'
ORDER BY devicename ASC;