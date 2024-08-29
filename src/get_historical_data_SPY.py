import pandas as pd
import duckdb
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
import os
from utils import remove_duplicates_sql, get_symbols_SPY
from pytz import timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = os.getenv("DATA_PATH")
HOME_PATH = os.getenv("HOME_PATH")

os.chdir(HOME_PATH)

timeframe=TimeFrame(1, TimeFrameUnit.Minute) # Intraday 1Min data
start_date="2016-01-01" # Alpaca markets API doesn't go further in time

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

def save_stock_data(df, db_name):
    symbols = " ".join(df.reset_index()["symbol"].unique())
    df.to_parquet(DATA_PATH + f"parquet_files/{symbols}.parquet", index=False)
    print(f"--> {symbols} symbol saved in: {DATA_PATH}")
    print(f"--> Timeframe: {start_date} - Latest available")

def main():
    # Get all S&P500 symbols
    symbols_SPY = get_symbols_SPY()

    # Check what symbols are already downloaded
    current_symbols = []
    for filename in os.listdir(DATA_PATH + 'parquet_files/'):
        if os.path.isfile(DATA_PATH + 'parquet_files/' + filename):
            symbol_name = os.path.splitext(filename)[0]
            current_symbols.append(symbol_name)

    print(f"Symbols already stored (N={len(current_symbols)}): {current_symbols}")

    # Download the rest
    symbols = list(set(symbols_SPY) - set(current_symbols))
    for symbol in symbols:
        df = get_stock_data(symbol)
        save_stock_data(df, "Stocks")

    # If there is no symbols left to be downloaded, stack them in a db
    if len(symbols) == 0:
        print("All symbols are already downloaded. Creating a unique parquet file with all the symbols...")
        duckdb.query('''
            COPY (SELECT * FROM read_parquet('{0}parquet_files/*.parquet'))
            TO '{0}spy_intraday_1M.parquet'
            (FORMAT 'parquet')
        '''.format(DATA_PATH))

        print(f"--> All SPY symbols saved as: {DATA_PATH}spy_intraday_1M.parquet")

if __name__== "__main__":
    main()
