import psycopg2.pool
import requests
import threading
import datetime
import os
import json
import logging


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

COINMARKETCAP_COLLECTOR_TOPIC = os.getenv("COINMARKETCAP_COLLECTOR_TOPIC")
COINMARKETCAP_COLLECTOR_INTERVAL = int(os.getenv("COINMARKETCAP_COLLECTOR_INTERVAL", 60))

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CP_MIN_CONN = int(os.getenv("DB_CP_MIN_CONN", 1))
DB_CP_MAX_CONN = int(os.getenv("DB_CP_MAX_CONN", 10))

cp = psycopg2.pool.SimpleConnectionPool(DB_CP_MIN_CONN, DB_CP_MAX_CONN, dbname=DB_NAME, user=DB_USER,
                                        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

logger = logging.getLogger('data_collector')
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
logger.addHandler(handler)

def retrieve_coin_market_cap_data():
    logging.debug("Retrieving coinmarketcap data.")
    try:
        r = requests.get("https://api.coinmarketcap.com/v1/ticker/", params={"limit": 0})
        data = r.json()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Retrieved data from coinmarketcap: %s" % json.dumps(data))
        result = {"data": data, "collected_datetime": datetime.datetime.utcnow().__str__()}
    except:
        logger.exception("Exception occurred while retrieving coinmarketcap data.")
        result = None

    return result


def save_coin_market_cap_data(data):
    logger.debug("Saving coinmarketcap data")
    insert_sql = "INSERT INTO COINMARKETCAP(id, name, symbol, rank, price_usd, price_btc, volume_24h_usd, " \
                 "market_cap_usd, available_supply, total_supply, max_supply, percent_change_1h, percent_change_24h, " \
                 "percent_change_7d, last_updated, collected_datetime) SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                 "%s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM COINMARKETCAP WHERE symbol = %s AND " \
                 "last_updated = %s)"
    conn = cp.getconn()
    try:
        with conn.cursor() as curs:
            for item in data["data"]:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("Inserting coinmarketcap item: %s" % json.dumps(item))
                # Use another try block here so if one record insert fails, we continue saving the rest.
                try:
                    curs.execute(insert_sql, (item["id"], item["name"], item["symbol"], item["rank"], item["price_usd"],
                                          item["price_btc"], item["24h_volume_usd"], item["market_cap_usd"],
                                          item["available_supply"], item["total_supply"], item["max_supply"],
                                          item["percent_change_1h"], item["percent_change_24h"],
                                          item["percent_change_7d"], item["last_updated"], data["collected_datetime"],
                                          item["symbol"], item["last_updated"]))
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    logger.exception("Error occurred while saving coinmarketcap data record.")
    except Exception as e:
        logger.exception("Error occurred while saving coinmarketcap data.")
    finally:
        cp.putconn(conn)


def collect_coin_market_cap():
    logger.debug("Collecting coin market cap data")
    try:
        data = retrieve_coin_market_cap_data()
        save_coin_market_cap_data(data)
    finally:
        logger.debug("Scheduling next execution of collect_coin_market_cap()")
        threading.Timer(COINMARKETCAP_COLLECTOR_INTERVAL, collect_coin_market_cap).start()

logger.info("Data collector started.")
collect_coin_market_cap()
