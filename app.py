from flask import Flask, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/get_exchange_rate_data')
def get_exchange_rate_data():
    conn = sqlite3.connect('databases/social_indicators.db')
    cursor = conn.cursor()

    # Calculate the date 15 days ago
    date_15_days_ago = datetime.now() - timedelta(days=15)
    date_15_days_ago_str = date_15_days_ago.strftime('%Y-%m-%d')

    # Query the database for the last 15 days of exchange rate data
    cursor.execute('''
        SELECT ID_tie_date, F_bcra_dolar
        FROM FT_BCRA_dolar
        WHERE ID_tie_date >= ? AND F_bcra_dolar IS NOT NULL
        ORDER BY ID_tie_date DESC
        LIMIT 15
    ''', (date_15_days_ago_str,))

    rows = cursor.fetchall()
    conn.close()

    # Convert the rows to a list of dictionaries
    exchange_rate_data = [{'date': row[0], 'rate': row[1]} for row in rows]

    return jsonify(exchange_rate_data)

if __name__ == '__main__':
    app.run(debug=True)