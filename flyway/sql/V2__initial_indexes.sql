CREATE INDEX idx_symbol ON COINMARKETCAP (symbol);
CREATE INDEX idx_last_updated on COINMARKETCAP (last_updated);
CREATE INDEX idx_collected_datetime on COINMARKETCAP(collected_datetime);