import pandas as pd
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pytz import timezone
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest
import duckdb
import time
import argparse

load_dotenv()

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = os.getenv("DATA_PATH_APP")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Update stock data with configurable time delta')
    parser.add_argument('--time_delta', type=float, default=1.2,
                      help='Time delta in hours (default: 1.2)')
    return parser.parse_args()

def get_symbols_SPY():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0].sort_values(by="Symbol")
    return dict(zip(df["Symbol"], df["Security"])), list(df["Symbol"])

def get_updated_stock_data(symbols):
    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    print(f"Getting the symbols from Alpaca Markets...")
    request_parameters = StockBarsRequest(
                    symbol_or_symbols= symbols,
                    timeframe=TimeFrame(1, TimeFrameUnit.Minute),
                    start=pd.to_datetime(start_date).tz_convert('America/New_York'),\
                    adjustment = "all",
                    )
    df = data_client.get_stock_bars(request_parameters).df.reset_index()

    return df

def save_updated_stock_data(df, symbols):
    start_time = time.time()

    need_to_update_symbols = df.reset_index()["symbol"].unique() if len(df) > 0 else []
    no_need_to_update_symbols =[symbol for symbol in symbols if symbol not in need_to_update_symbols]

    if len(need_to_update_symbols) > 0:
        print(f"Alpaca found new data for {len(need_to_update_symbols)} symbols")
        # Updating CSV files that need to be updated
        for symbol in need_to_update_symbols:
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

        # Touching CSV files that DO NOT need to be updated
        print(f"Alpaca didn't found new data for {len(no_need_to_update_symbols)} symbols")
        for symbol in no_need_to_update_symbols:
            print(f"Touching: {symbol}...")
            filename = f"{symbol}.csv"
            try:
                file_path = os.path.join(DATA_PATH, filename)
                os.utime(file_path, None)
            except OSError as e:
                print(f"Error touching file for {symbol}: {e}")

        # Update the consolidated CSV file
        print(f"Updating the consolidated CSV file with all the data...")
        consolidated_file_name = '503 S&P Symbols'

        csv_files = [f for f in os.listdir(DATA_PATH) if f.endswith('.csv')]
        csv_filepaths = ','.join([f"'{DATA_PATH}/{f}'" for f in csv_files])

        duckdb.sql("SET threads TO 4")
        duckdb.query(f"""
        COPY (
            SELECT * FROM read_csv_auto([{csv_filepaths}])
        ) TO '{DATA_PATH}/temp_{consolidated_file_name}.CSV'
        WITH (FORMAT 'CSV', HEADER)
        """)

        os.rename(f'{DATA_PATH}/temp_{consolidated_file_name}.CSV', f'{DATA_PATH}/{consolidated_file_name}.CSV')

    else:
        print(f"No new data to be added")
        # Touch all files if no need to update (e.g. weekends)
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv') or file.endswith('.CSV'):
                    os.utime(os.path.join(DATA_PATH, file), None)


    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    print(f"--> Execution time: {execution_time} seconds")
    print(f"--> Data path: {DATA_PATH}")
    print(f"--> Dates added: {start_date} - Latest available")

def main():

    args = parse_arguments()
    delta = timedelta(hours=args.time_delta)
    global start_date
    start_date = datetime.now(timezone('US/Eastern')) - delta

    print("Time delta:", delta)

    symbols = get_symbols_SPY() # 0 for dict, 1 for list
    df = get_updated_stock_data(symbols[1])
    save_updated_stock_data(df, symbols=symbols[1])

if __name__ == "__main__":
    main()
