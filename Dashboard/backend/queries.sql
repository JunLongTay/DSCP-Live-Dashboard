-- name: compost-npk-bucketed
SELECT
  to_timestamp(
    floor(extract(epoch FROM dd.devicetimestamp) / ($1 * 60))
    * ($1 * 60)
  ) AT TIME ZONE 'UTC' AS timestamp,
  AVG(CASE WHEN sd.sensorid = 12 THEN sd.value::float END) AS nitrogen,
  AVG(CASE WHEN sd.sensorid = 13 THEN sd.value::float END) AS phosphorus,
  AVG(CASE WHEN sd.sensorid = 14 THEN sd.value::float END) AS potassium
FROM devicedata dd
JOIN sensordata sd
  ON sd.devicedataid = dd.devicedataid
WHERE sd.sensorid IN (12, 13, 14)
  AND dd.devicetimestamp >= NOW() - ($2 || ' minutes')::interval
GROUP BY timestamp
ORDER BY timestamp DESC;

-- name: soil-temp-co2-bucketed
SELECT
  to_timestamp(
    floor(extract(epoch FROM dd.devicetimestamp) / ($1 * 60))
    * ($1 * 60)
  ) AT TIME ZONE 'UTC' AS timestamp,
  AVG(CASE WHEN sd.sensorid = 8 THEN sd.value::float END) AS soil_temp,
  AVG(CASE WHEN sd.sensorid = 1 THEN sd.value::float END) AS co2
FROM devicedata dd
JOIN sensordata sd
  ON sd.devicedataid = dd.devicedataid
WHERE sd.sensorid IN (8, 1)
  AND dd.devicetimestamp >= NOW() - ($2 || ' minutes')::interval
GROUP BY timestamp
ORDER BY timestamp DESC;

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