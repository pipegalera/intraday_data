import pandas as pd
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv()
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
start_date = datetime.now(timezone('US/Eastern')) - timedelta(hours=5)

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

    print(f"Updating the CSV files with the new data...")
    start_time = time.time()

    # Update each symbol CSV file
    symbols = df.reset_index()["symbol"].unique()
    consolidated_file_name = '503 S&P Symbols - All data'
    for symbol in symbols:
        print(f"Updating: {symbol}...")
        combined_data = (f'''
                   WITH combined_data AS (
                       SELECT * FROM df WHERE symbol = '{symbol}'
                       UNION
                       SELECT * FROM '{DATA_PATH}/{symbol}.csv'
                       ORDER BY timestamp
                   )
                   SELECT * FROM combined_data
               ''')
        # Write over every CSV file
        duckdb.query(f'''
                COPY ({combined_data})
                TO '{DATA_PATH}/{symbol}.csv'
                (FORMAT 'CSV', HEADER)
            ''')

    # Update the consolidated CSV file
    print(f"Updating the consolidated CSV file with all the data...")
    duckdb.query(f"""
    COPY (
        SELECT * FROM read_csv_auto('{DATA_PATH}/*.csv')
    ) TO '{DATA_PATH}/503 S&P Symbols - All data.CSV'
    WITH (FORMAT 'CSV', HEADER)
    """)
    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    print(f"--> Execution time: {execution_time} seconds")
    print(f"--> Data path: {DATA_PATH}")
    print(f"--> Timeframe added: {start_date} - Latest available")


def main():
    spy_symbols = [os.path.splitext(file)[0] for file in os.listdir(DATA_PATH) if file.endswith('.csv')]
    df = get_updated_stock_data(spy_symbols)
    save_updated_stock_data(df)

if __name__ == "__main__":
    main()
