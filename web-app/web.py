from flask import Flask, request, jsonify
import psycopg2.pool
import os
import logging


DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CP_MIN_CONN = int(os.getenv("DB_CP_MIN_CONN", 1))
DB_CP_MAX_CONN = int(os.getenv("DB_CP_MAX_CONN", 10))

cp = psycopg2.pool.SimpleConnectionPool(DB_CP_MIN_CONN, DB_CP_MAX_CONN, dbname=DB_NAME, user=DB_USER,
                                        password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger = logging.getLogger('data_collector')
logger.setLevel(LOG_LEVEL)
handler = logging.StreamHandler()
logger.addHandler(handler)

app = Flask(__name__)


def to_int(str_val, default, min_val=None, max_val=None):
    try:
        result = int(str_val)
        if (min_val is not None and result < min_val) or (max_val is not None and result > max_val):
            return default
        return result
    except Exception:
        return default


@app.route("/api/v1/ticker")
def ticker():
    limit = to_int(request.args.get('limit', None), 10, min_val=1, max_val=100)
    offset = to_int(request.args.get('offset', None), 0, min_val=0)
    sql = "SELECT id, name, symbol, rank, price_usd, price_btc, volume_24h_usd, market_cap_usd, available_supply, total_supply, max_supply, percent_change_1h, percent_change_24h, percent_change_7d, last_updated, collected_datetime " \
          "FROM (SELECT id, name, symbol, rank, price_usd, price_btc, volume_24h_usd, market_cap_usd, available_supply, total_supply, max_supply, percent_change_1h, percent_change_24h, percent_change_7d, last_updated, collected_datetime, rank() OVER (PARTITION BY symbol ORDER BY last_updated DESC) AS pos FROM coinmarketcap WHERE collected_datetime > now() - interval '10 minutes') AS a " \
          "WHERE a.pos = 1 " \
          "AND rank BETWEEN %s AND %s " \
          "ORDER BY rank;"
    response = {}
    conn = cp.getconn()
    try:
        with conn.cursor() as curs:
            curs.execute(sql, (offset + 1, offset + limit))
            response = {"data": [{"id": r[0], "name": r[1], "symbol": r[2], "rank": r[3], "price_usd": r[4], "price_btc": r[5], "volume_24h_usd": r[6], "market_cap_usd": r[7], "available_supply": r[8], "total_supply": r[9], "max_supply": r[10], "percent_change_1h": r[11], "percent_change_24h": r[12], "percent_change_7d": r[13], "last_updated": r[14], "collected_datetime": r[15]} for r in curs]}

    except Exception as e:
        logger.exception("Error occurred while retrieving coinmarketcap data.")
    finally:
        cp.putconn(conn)

    return jsonify(response)
