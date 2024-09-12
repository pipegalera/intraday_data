import pandas as pd
import duckdb
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
import os
from pytz import timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = os.getenv("DATA_PATH")

timeframe=TimeFrame(1, TimeFrameUnit.Minute) # Intraday 1Min data
start_date="2016-01-01" # Alpaca markets API doesn't go further in time

def get_symbols_SPY():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0]
    return dict(zip(df["Symbol"], df["Security"]))

def get_stock_data(symbols,
                 timeframe=timeframe,
                 start_date=start_date):

    # Create a data client to fetch historical data
    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    request_parameters = StockBarsRequest(
                    symbol_or_symbols=symbols,
                    timeframe=timeframe,
                    start=pd.to_datetime(start_date).tz_localize('America/New_York')                    )

    # Fetch data and convert to dataframe
    print(f"Getting Alpaca Markets 1Min intraday data for {symbols} ...")
    df = data_client.get_stock_bars(request_parameters).df.reset_index()

    return df

def save_stock_data(df):
    symbols = " ".join(df.reset_index()["symbol"].unique())
    df.to_csv(DATA_PATH + f"/{symbols}.csv", index=False)
    print(f"--> {symbols} symbol saved in: {DATA_PATH}")
    print(f"--> Timeframe: {start_date} - Latest available")

def main():
    # Get all S&P500 symbols
    symbols_SPY = sorted(get_symbols_SPY().keys())

    # Check what symbols are already downloaded
    current_symbols = []
    for filename in os.listdir(DATA_PATH):
        if os.path.isfile(DATA_PATH + '/' + filename):
            symbol_name = os.path.splitext(filename)[0]
            current_symbols.append(symbol_name)

    print(f"Symbols already stored (N={len(current_symbols)}): {current_symbols}")

    # Download the rest
    symbols = list(set(symbols_SPY) - set(current_symbols))
    for symbol in symbols:
        df = get_stock_data(symbol)
        save_stock_data(df)

    # If there is no symbols left to be downloaded, stack them in a single file
    consolidated_file_name = '503 S&P Symbols - All data'
    if len(symbols) == 0:
        print("All symbols are already downloaded. Creating a unique CSV file with all the symbols...")
        duckdb.query('''
            COPY (SELECT * FROM read_csv('{0}/*.csv'))
            TO '{0}/{1}.CSV'
            (FORMAT 'CSV')
        '''.format(DATA_PATH, consolidated_file_name))

        print(f"--> All SPY symbols saved as: {DATA_PATH}/{consolidated_file_name}.CSV")

if __name__== "__main__":
    main()
