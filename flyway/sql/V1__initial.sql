CREATE TABLE COINMARKETCAP (
    id varchar(50),
    name varchar(50),
    symbol varchar(50),
    rank integer,
    price_usd money,
    price_btc numeric(25, 8),
    volume_24h_usd money,
    market_cap_usd money,
    available_supply numeric(25, 8),
    total_supply numeric(25, 8),
    max_supply numeric(25, 8),
    percent_change_1h numeric(11, 2),
    percent_change_24h numeric(11, 2),
    percent_change_7d numeric(11, 2),
    last_updated bigint,
    collected_datetime timestamp
);

