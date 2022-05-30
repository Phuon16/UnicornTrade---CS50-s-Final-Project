import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot
import matplotlib.pyplot as plt
import datetime
from pycoingecko import CoinGeckoAPI
from mplfinance.original_flavor import candlestick2_ohlc
import plotly

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
    'symbol': symbol,
    'convert':'USD'
    }

    # Get API of user
    coinmarketcap_api_key = os.environ.get("API_KEY")
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': coinmarketcap_api_key,
    }

    session = Session()
    session.headers.update(headers)


    # Parse response
    try:
        response = session.get(url, params=parameters)
        quote = response.json()
        return {
            "name": quote["data"][symbol]["name"],
            "price": float(quote["data"][symbol]["quote"]["USD"]["price"]),
            "symbol": quote["data"][symbol]["symbol"],
            "volumne": '{:,}'.format(round(quote["data"][symbol]["quote"]["USD"]["volume_24h"])),
            "marketcap": '{:,}'.format(round(quote["data"][symbol]["quote"]["USD"]["market_cap"])),
            "fdv": '{:,}'.format(round(quote["data"][symbol]["quote"]["USD"]["fully_diluted_market_cap"]))
        }
    except (KeyError, TypeError, ValueError, ConnectionError, Timeout, TooManyRedirects):
        return None


def usdt(value):
    """Format value as USDT."""
    return f"${value:,.2f} USDT"

def chart(coin_name):
    # id is the name of the coin you want, vs_currency is the currency you want the price in, and days is how many days back from today you want.
    cg = CoinGeckoAPI()
    bitcoin_data = cg.get_coin_market_chart_by_id(id=coin_name, vs_currency='usd', days=30)

    bitcoin_price_data = bitcoin_data['prices']

    # turn data into a Panda dataframe
    data = pd.DataFrame(bitcoin_price_data, columns=['TimeStamp', 'Price'])

    # convert the timestamp to date
    data['date'] = data['TimeStamp'].apply(lambda d: datetime.date.fromtimestamp(d/1000.0))

    # group by the date, find min max open and close for candlesticks
    candlestick_data = data.groupby(data.date,as_index=False).agg({"Price": ['min','max','first','last']})

    # use plotly to create Candlestick Chart
    try:
        fig = go.Figure(data=[go.Candlestick(x=candlestick_data['date'],
                    open=candlestick_data['Price']['first'],
                    high=candlestick_data['Price']['max'],
                    low=candlestick_data['Price']['min'],
                    close=candlestick_data['Price']['last'])
                            ])

        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
        fig.update_layout(yaxis_title = "Price (USD)", xaxis_title = "Date")
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    except (KeyError, TypeError, ValueError, ConnectionError, Timeout, TooManyRedirects):
        return None