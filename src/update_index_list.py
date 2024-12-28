import os
import json
from dotenv import load_dotenv
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.requests import StockBarsRequest

load_dotenv()

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = os.getenv("DATA_PATH")

def get_symbols_SPY():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    df = pd.read_html(url)[0].sort_values(by="Symbol")
    return dict(zip(df["Symbol"], df["Security"])), df["Symbol"].tolist()

def get_stock_data(symbol: str, start_date: str):

    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    request_parameters = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame(1, TimeFrameUnit.Minute),
                    start=pd.to_datetime(start_date).tz_localize('America/New_York'),
                    adjustment = "all",)

    # Fetch data and convert to dataframe
    print(f"Getting Alpaca Markets 1Min intraday data for {symbol} ...")
    df = data_client.get_stock_bars(request_parameters).df.reset_index()

    return df

def delete_oudated_symbols(current_symbols, updated_symbols):
    # Remove CSV files for symbols no longer in S&P 500.
    symbol_to_delete = list(set(current_symbols) - set(updated_symbols))
    print(f"Symbols outdated: {symbol_to_delete}")

    for symbol in symbol_to_delete:
        print(f"Deleating outdated symbol: {symbol}")
        file_path = os.path.join(DATA_PATH, f"{symbol}.csv")
        os.remove(file_path)

def add_updated_symbols(current_symbols: list,
                        updated_symbols: list,
                        start_date: str):
    # Add new symbols that have been added to S&P 500.
    symbol_to_add = list(set(updated_symbols) - set(current_symbols))
    print(f"Symbols to be added: {symbol_to_add}")

    for symbol in symbol_to_add:
        df = get_stock_data(symbol, start_date)

        df.to_csv(f"{DATA_PATH}/{symbol}.csv", index=False)
        print(f"--> {symbol} symbol saved in: {DATA_PATH}")
        print(f"--> Timeframe: {start_date} - Latest available")

def main():
    start_date = "2024-01-01"
    updated_dict_symbols , updated_symbols = get_symbols_SPY()
    current_symbols = [f.removesuffix('.csv') for f in os.listdir(DATA_PATH) if f.endswith('.csv')]

    delete_oudated_symbols(current_symbols, updated_symbols)
    add_updated_symbols(current_symbols, updated_symbols, start_date)

    # Save updated symbols dictionary to file
    with open("app/sp500_symbols.json", "w") as f:
        json.dump(updated_dict_symbols, f)

if __name__ == "__main__":
    main()
