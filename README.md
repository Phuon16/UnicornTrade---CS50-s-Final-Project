# UnicornTrade
#### Video Demo:  <https://youtu.be/8Mt6RYBBJNg>
#### Description:

## Definition
>Demo accounts are where prospective investors can practice trading and learn systems before trading with real money. Many businesses offer these online programs for beginner investors to get a feel for what it’s like to trade on real markets—without the impending risk.

>A cryptocurrency, crypto-currency, crypto, or coin is a digital currency designed to work as a medium of exchange through a computer network that is not reliant on any central authority, such as a government or bank, to uphold or maintain it.

# How UnicornTrade Works
Get started!

## Register

Create a new account with unique account name to enjoy the demo trading website - UnicornTrade.
On the registration page, enter your username, create a password for your account then click "Register".

If you leave the name or password/ retype password blanks, the page will show errors.

## Log In/ Log Out

Use the registed account then log in to UnicornTrade website.
If you haven't sign up for an account yet, please click on "New member?" or Registration page.

## Quote Coin Price

You can input the coin symbol (reference to CoinMarketcap) to see coin chart history 30 days and current price (change every 1 minute). The data was provided by CoinMarketcap and CoinGecko.
In the coin chart, it shows candlestick for each day: the opening, closing, highest and lowest price.

## Features (Buy/Sell)

Each account will be given $100K cash at the beginning, enjoy trading the coin with zero price.
You can buy or sell any coin listed on CoinMarketcap, then track your current coin price on the index page

## Add to Favorites

Build your own personalized cryptocurrency watchlist.
This feature allows you to add any coins you want to follow on the coin list.
Once the coin is added, it will update every 1 min:
- Price
- Market Capital
- 24h Trading Volume
- Fully Dilluted Market Capital

## History

A table that remembers your trading history with price, amount and time.

# The Designation
UnicornTrade was built in:
- HTML, CSS
- Flask, pyplot, pandas, numpy: I choose Python Flask and Pyplot to easily visualize the chart of coin history and data API
- Bootstrap 5: I find it better to use bootstrap existing CSS design for more convenience

# API
- CoinMarketCap API <https://coinmarketcap.com/api/documentation/v1/#>

Need to register for API key!

>The CoinMarketCap API is a suite of high-performance RESTful JSON endpoints that are specifically designed to meet the mission-critical demands of application developers, data scientists, and enterprise business platforms.

>Returns the latest market quote for 1 or more cryptocurrencies. Use the "convert" option to return market values in multiple fiat and cryptocurrency conversions in the same call.

- CoinGecko API <https://www.coingecko.com/en/api/documentation>
<Python
https://github.com/man-c/pycoingecko>

Free API, Reliable, Comprehensive

>Power your applications with CoinGecko’s independently sourced crypto data such as live prices, trading volume, exchange volumes, trading pairs, historical data, contract address data, crypto categories, crypto derivatives, images and more.

>Get historical market data include price, market cap, and 24h volume (granularity auto)
Minutely data will be used for duration within 1 day, Hourly data will be used for duration between 1 day and 90 days, Daily data will be used for duration above 90 days.




Made with ♥ by Phuon16