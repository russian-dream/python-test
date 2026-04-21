from flask import Flask, request, jsonify, abort
import sqlite3
import os
import logging

app = Flask(__name__)
app.config['DB_PATH'] = os.environ.get('DB_PATH', 'products.db')

# SQL-запросы — константы модуля, не зависят от пользовательского ввода
SEARCH_PRODUCTS_SQL = "SELECT id, name, price FROM products WHERE name LIKE :pattern"

PRICE_DISCOUNT_THRESHOLD = 100
DISCOUNT_RATE = 0.1

logger = logging.getLogger(__name__)


@app.route('/search')
def search_products():
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) > 100:
        abort(400, "Invalid search term")

    like_pattern = '%' + search_term + '%'

    with sqlite3.connect(app.config['DB_PATH']) as conn:
        cursor = conn.cursor()
        cursor.execute(SEARCH_PRODUCTS_SQL, {"pattern": like_pattern})
        results = cursor.fetchall()

    return jsonify(results)


def _item_cost(item):
    price = item.get('price')
    if price is None:
        logger.warning("Item without price: %s", item)
        return 0
    if price > PRICE_DISCOUNT_THRESHOLD:
        return price * (1 - DISCOUNT_RATE)
    return price


def calculate_price(items):
    return sum(_item_cost(i) for i in items)


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
