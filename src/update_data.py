import pandas as pd
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
from utils import spy_symbols
from pytz import timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
import duckdb
import time

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = os.getenv("DATA_PATH")


timeframe=TimeFrame(1, TimeFrameUnit.Minute)
start_date = datetime.now(timezone('US/Eastern')) - timedelta(days=1)

def get_updated_stock_data(symbols):
    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    print(f"Getting the symbols from Alpaca Markets...")
    request_parameters = StockBarsRequest(
                    symbol_or_symbols=symbols,
                    timeframe=timeframe,
                    start=pd.to_datetime(start_date).tz_convert('America/New_York'),
                    )
    df = data_client.get_stock_bars(request_parameters).df.reset_index()

    return df

def save_updated_stock_data(df):
    # Get the symbols
    symbols = df.reset_index()["symbol"].unique()
    print(f"Updating the parquet files and SQL database with the new data...")
    start_time = time.time()
    for symbol in symbols:
        print(f"Updating: {symbol}...")
        combined_data = (f'''
            WITH combined_data AS (
                SELECT * FROM df WHERE symbol = '{symbol}'
                UNION
                SELECT * FROM '{DATA_PATH}parquet_files/{symbol}.parquet'
                ORDER BY timestamp
            )
            SELECT * FROM combined_data
        ''')
        # Write over every parquet file
        duckdb.query(f'''
            COPY ({combined_data})
            TO '{DATA_PATH}parquet_files/{symbol}.parquet'
            (FORMAT 'parquet')
        ''')

        # Write over the general parquet file
        duckdb.query(f'''
            COPY ({combined_data})
            TO '{DATA_PATH}parquet_files/spy_intraday_1M.parquet'
            (FORMAT 'parquet')
        ''')

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    print(f"--> Execution time: {execution_time} seconds")
    print(f"--> Data path: {DATA_PATH}")
    print(f"--> Timeframe added: {start_date} - Latest available")



def main():
    df = get_updated_stock_data(spy_symbols)
    save_updated_stock_data(df)

if __name__ == "__main__":
    main()
