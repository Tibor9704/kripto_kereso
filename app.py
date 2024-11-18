import requests
from flask import Flask, render_template, request
import random
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime
import mysql.connector
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# API kulcs és URL
api_url = "https://min-api.cryptocompare.com/data/price"
api_key = "4b5dbfb308cbbe4c4ae2b2797498d1bba0c545e10a4404c3f0e22b80e49609e7"  

# Keresett valuták listája
currencies = [
    'BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOGE', 'SOL', 'MATIC', 'DOT',
    'TRX', 'BNB', 'AVAX', 'FTM', 'SHIB', 'MANA', 'NEAR', 'LDO', 'APE', 'FTT', 'CHZ',
    'ATOM', 'SAND', 'GALA', 'ENJ', 'XLM', 'ZRX', 'FIL', 'YFI', 'AAVE', 'CRV', 'MKR',
    'RUNE', 'LRC', 'REN', 'BAT', 'DOGE', 'CRO', 'VET', 'EOS', 'XTZ', 'ALGO', 'MKR',
    'DASH', 'QKC', 'ICX', 'ZEC', 'MITH', 'STMX', 'GRT', 'NKN', 'STPT', 'SKL', 'UNI',
    'SUSHI', '1INCH', 'PAXG', 'USTC', 'MITH', 'KSM', 'FIL', 'LTC', 'QKC'
]

# Adatbázis kapcsolódás
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',  
        user='root',       
        password='',        
        database='crypto'   
    )

# API adat lekérdezése és mentése
def save_price_to_db(currency, price, percent_change, table):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table} (currency, price_usd, percent_change) VALUES (%s, %s, %s)", (currency, price, percent_change))
    conn.commit()
    cursor.close()
    conn.close()

# API hívás és árfolyam lekérdezés egy adott valutára
def get_price_from_api(currency):
    response = requests.get(api_url, params={
        'fsym': currency,
        'tsyms': 'USD',
        'api_key': api_key
    })
    if response.status_code == 200:
        data = response.json()
        return data.get('USD')
    return None

# API hívás és árfolyam lekérdezés 24 órás történetre
def get_historical_data(currency):
    url = "https://min-api.cryptocompare.com/data/v2/histohour"
    params = {
        'fsym': currency,
        'tsym': 'USD',
        'limit': 24,  
        'api_key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {'time': entry['time'], 'close': round(entry['close'], 2)}
            for entry in data['Data']['Data']
        ]
    return None

# Véletlenszerű árfolyamok lekérése néhány valutára
def get_random_prices():
    currencies = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOGE', 'SOL', 'MATIC', 'DOT']
    random_currencies = random.sample(currencies, 5)  
    prices = {}

    with ThreadPoolExecutor() as executor:
        futures = {currency: executor.submit(fetch_price_for_currency, currency) for currency in random_currencies}
        for currency, future in futures.items():
            price_data = future.result()
            if price_data:
                prices[currency] = price_data
    return prices

def fetch_price_for_currency(currency):
    current_price = get_price_from_api(currency)
    if current_price:
        historical_data = get_historical_data(currency)
        if historical_data and len(historical_data) > 1:
            previous_price = historical_data[-2]['close']  

            if previous_price != 0:
                percent_change = ((current_price - previous_price) / previous_price) * 100
                return {'price': current_price, 'percent_change': percent_change}
            else:
                return {'price': current_price, 'percent_change': 0}  
    return None

# Legnagyobb veszteségek és nyereségek lekérdezése és mentése
def get_top_10_losers():
    prices = []
    with ThreadPoolExecutor() as executor:
        futures = {currency: executor.submit(fetch_price_for_currency, currency) for currency in currencies}
        for currency, future in futures.items():
            price_data = future.result()
            if price_data:
                prices.append((currency, price_data['price'], price_data['percent_change']))
    
    prices.sort(key=lambda x: x[2])  
    top_10_losers = prices[:10]
    for loser in top_10_losers:
        save_price_to_db(loser[0], loser[1], loser[2], 'losses')
    return top_10_losers

def get_top_10_gainers():
    prices = []
    with ThreadPoolExecutor() as executor:
        futures = {currency: executor.submit(fetch_price_for_currency, currency) for currency in currencies}
        for currency, future in futures.items():
            price_data = future.result()
            if price_data and price_data['percent_change'] > 0:
                prices.append((currency, price_data['price'], price_data['percent_change']))

    prices.sort(key=lambda x: x[2], reverse=True)  
    top_10_gainers = prices[:10]
    for winner in top_10_gainers:
        save_price_to_db(winner[0], winner[1], winner[2], 'gains')
    
    return top_10_gainers

# Főoldal és keresés
@app.route('/', methods=['GET', 'POST'])
def index():
    price = None
    currency = None
    error = None
    plot_div = None
    percent_change = None

    if request.method == 'POST':
        currency = request.form['currency'].upper()  
        price = get_price_from_api(currency)
        if price is not None:
            # 24 órás történeti adatok lekérése a százalékos változáshoz
            historical_data = get_historical_data(currency)
            if historical_data and len(historical_data) > 1:
                previous_price = historical_data[-2]['close']  
                percent_change = ((price - previous_price) / previous_price) * 100
        else:
            error = f"Nincs adat a {currency} valutáról!"

        if historical_data:
            times = [entry['time'] for entry in historical_data]
            prices = [entry['close'] for entry in historical_data]
            times = [datetime.utcfromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S') for t in times]

            # Grafikon létrehozása
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=prices, mode='lines', name=f'{currency} Árfolyam'))
            fig.update_layout(
                title=f'{currency} 24 órás árfolyamváltozása',
                xaxis_title='Időpont',
                yaxis_title='Árfolyam (USD)',
                template='plotly_dark'
            )
            plot_div = json.dumps(fig, cls=PlotlyJSONEncoder)

    random_prices = get_random_prices()

    top_10_losers = None
    top_10_gainers = None
    if request.args.get('action') == 'losers':
        top_10_losers = get_top_10_losers()
    elif request.args.get('action') == 'gainers':
        top_10_gainers = get_top_10_gainers()

    return render_template(
        'index.html',
        price=price,
        currency=currency,
        error=error,
        random_prices=random_prices,
        plot_div=plot_div,
        top_10_losers=top_10_losers,
        top_10_gainers=top_10_gainers
    )

if __name__ == '__main__':
    app.run(debug=True)
