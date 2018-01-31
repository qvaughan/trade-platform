ALTER TABLE COINMARKETCAP
ALTER COLUMN price_usd TYPE NUMERIC(25,8) USING price_usd::numeric,
ALTER COLUMN volume_24h_usd TYPE NUMERIC(25,8) USING volume_24h_usd::numeric,
ALTER COLUMN market_cap_usd TYPE NUMERIC(25,8) USING market_cap_usd::numeric;

