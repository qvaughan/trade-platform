import psycopg2.pool
import requests
import threading
import datetime
import os
import traceback

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


def retrieve_coin_market_cap_data():
    try:
        r = requests.get("https://api.coinmarketcap.com/v1/ticker/", params={"limit": 0})
        data = r.json()
        result = {"data": data, "collected_datetime": datetime.datetime.utcnow().__str__()}
    except:
        traceback.print_exc()
        result = None

    return result


def save_coin_market_cap_data(data):
    insert_sql = "INSERT INTO COINMARKETCAP(id, name, symbol, rank, price_usd, price_btc, volume_24h_usd, " \
                 "market_cap_usd, available_supply, total_supply, max_supply, percent_change_1h, percent_change_24h, " \
                 "percent_change_7d, last_updated, collected_datetime) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, " \
                 "%s, %s, %s, %s, %s, %s, %s)"
    conn = cp.getconn()
    try:
        with conn.cursor() as curs:
            for item in data["data"]:
                curs.execute(insert_sql, (item["id"], item["name"], item["symbol"], item["rank"], item["price_usd"],
                                          item["price_btc"], item["24h_volume_usd"], item["market_cap_usd"],
                                          item["available_supply"], item["total_supply"], item["max_supply"],
                                          item["percent_change_1h"], item["percent_change_24h"],
                                          item["percent_change_7d"], item["last_updated"], data["collected_datetime"]))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cp.putconn(conn)


def collect_coin_market_cap():
    print("Collecting coin market cap data.")
    try:
        data = retrieve_coin_market_cap_data()
        save_coin_market_cap_data(data)
    finally:
        threading.Timer(COINMARKETCAP_COLLECTOR_INTERVAL, collect_coin_market_cap).start()
        print("Next run scheduled...")

collect_coin_market_cap()
