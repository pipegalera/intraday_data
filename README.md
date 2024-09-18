![EasyFinData.com](images/cover.png)

⚠️ DISCLAIMER ⚠️: This project is for educational and hobbyist purposes. If you are a company, please use production-ready financial API data services such as [IQFeed](https://www.iqfeed.net/), [PolygonIO](https://polygon.io/), or [Alpaca Markets](https://alpaca.markets/).

## What

[EasyFinData.com](https://EasyFinData.com) automatically collects 1Min intraday data of the S&P500 from `2016-01-01` until current date and serves them in convenient CSV files.

Its a very accessible gateway for intraday data for non-coders.

## Why

I couldn't find any easy, accesible, and free platform that provided intraday stock data files.

I figured that more people would have the same problem, so I try to solve it - e.g. see the [multiple reddit posts about intraday data](https://www.google.com/search?q=intraday+data+free+site%3Awww.reddit.com).

## How

The website is hosted in a [Hetzner VPS](https://www.hetzner.com/cloud/) in Germany. The data comes from [Alpaca Markets API](https://alpaca.markets/), and updated every hour
using their generous API free tier (limit 200calls/min) via [Cron jobs](https://en.wikipedia.org/wiki/Cron).

The entire source code of the website is completely transparent: Under `app` folder in this repo you can find the app, and under `src` the data collection and automation code.
