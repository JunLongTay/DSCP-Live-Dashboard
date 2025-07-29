-- name: compost-npk-bucketed
SELECT
  to_timestamp(
    floor(extract(epoch FROM dd.devicetimestamp) / ($1 * 60))
    * ($1 * 60)
  ) AT TIME ZONE 'Asia/Singapore' AS timestamp,
  d.devicename,
  AVG(CASE WHEN sd.sensorid = 12 THEN sd.value::float END) AS nitrogen,
  AVG(CASE WHEN sd.sensorid = 13 THEN sd.value::float END) AS phosphorus,
  AVG(CASE WHEN sd.sensorid = 14 THEN sd.value::float END) AS potassium
FROM devicedata dd
JOIN sensordata sd
  ON sd.devicedataid = dd.devicedataid
JOIN devices d ON dd.deviceid = d.deviceid
WHERE sd.sensorid IN (12, 13, 14)
  AND dd.devicetimestamp >= NOW() - ($2 || ' minutes')::interval
GROUP BY timestamp, d.devicename
ORDER BY timestamp DESC;

-- name: soil-temp-co2-bucketed
SELECT
  to_timestamp(
    floor(extract(epoch FROM dd.devicetimestamp) / ($1 * 60))
    * ($1 * 60)
  ) AT TIME ZONE 'Asia/Singapore' AS timestamp,
  d.devicename,
  AVG(CASE WHEN sd.sensorid = 8 THEN sd.value::float END) AS soil_temp,
  AVG(CASE WHEN sd.sensorid = 1 THEN sd.value::float END) AS co2
FROM devicedata dd
JOIN sensordata sd
  ON sd.devicedataid = dd.devicedataid
JOIN devices d ON dd.deviceid = d.deviceid
WHERE sd.sensorid IN (8, 1)
  AND dd.devicetimestamp >= NOW() - ($2 || ' minutes')::interval
GROUP BY timestamp, d.devicename
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
GROUP BY timestamp, d.devicename
ORDER BY timestamp DESC;

-- name: moisture-all-detailed
SELECT 
  to_timestamp(floor(extract('epoch' from dd.devicetimestamp) / ($1 * 60)) * ($1 * 60)) AT TIME ZONE 'UTC' AS timestamp,
  d.devicename,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Moisture') AS moisture,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Temperature') AS temperature,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Nitrogen') AS npk_n,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Phosphorus') AS npk_p,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'Soil Potassium') AS npk_k,
  AVG(sd.value::float) FILTER (WHERE s.sensor = 'CO2') AS co2
FROM devicedata dd
JOIN sensordata sd ON sd.devicedataid = dd.devicedataid
JOIN sensors s ON sd.sensorid = s.sensorid
JOIN devices d ON dd.deviceid = d.deviceid
WHERE dd.devicetimestamp >= NOW() - make_interval(mins := $2)
GROUP BY timestamp, d.devicename
ORDER BY timestamp DESC;

-- name: device-names
SELECT devicename
FROM devices
ORDER BY devicename ASC;

-- name: np-devices
SELECT devicename
FROM devices
ORDER BY devicename ASC;

