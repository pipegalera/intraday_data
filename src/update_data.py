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
import argparse

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
DATA_PATH = "/app/storage/"

symbols_names = {'MMM': '3M',
 'AOS': 'A. O. Smith',
 'ABT': 'Abbott Laboratories',
 'ABBV': 'AbbVie',
 'ACN': 'Accenture',
 'ADBE': 'Adobe Inc.',
 'AMD': 'Advanced Micro Devices',
 'AES': 'AES Corporation',
 'AFL': 'Aflac',
 'A': 'Agilent Technologies',
 'APD': 'Air Products',
 'ABNB': 'Airbnb',
 'AKAM': 'Akamai Technologies',
 'ALB': 'Albemarle Corporation',
 'ARE': 'Alexandria Real Estate Equities',
 'ALGN': 'Align Technology',
 'ALLE': 'Allegion',
 'LNT': 'Alliant Energy',
 'ALL': 'Allstate',
 'GOOGL': 'Alphabet Inc. (Class A)',
 'GOOG': 'Alphabet Inc. (Class C)',
 'MO': 'Altria',
 'AMZN': 'Amazon',
 'AMCR': 'Amcor',
 'AEE': 'Ameren',
 'AAL': 'American Airlines Group',
 'AEP': 'American Electric Power',
 'AXP': 'American Express',
 'AIG': 'American International Group',
 'AMT': 'American Tower',
 'AWK': 'American Water Works',
 'AMP': 'Ameriprise Financial',
 'AME': 'Ametek',
 'AMGN': 'Amgen',
 'APH': 'Amphenol',
 'ADI': 'Analog Devices',
 'ANSS': 'Ansys',
 'AON': 'Aon',
 'APA': 'APA Corporation',
 'AAPL': 'Apple Inc.',
 'AMAT': 'Applied Materials',
 'APTV': 'Aptiv',
 'ACGL': 'Arch Capital Group',
 'ADM': 'Archer Daniels Midland',
 'ANET': 'Arista Networks',
 'AJG': 'Arthur J. Gallagher & Co.',
 'AIZ': 'Assurant',
 'T': 'AT&T',
 'ATO': 'Atmos Energy',
 'ADSK': 'Autodesk',
 'ADP': 'Automatic Data Processing',
 'AZO': 'AutoZone',
 'AVB': 'AvalonBay Communities',
 'AVY': 'Avery Dennison',
 'AXON': 'Axon Enterprise',
 'BKR': 'Baker Hughes',
 'BALL': 'Ball Corporation',
 'BAC': 'Bank of America',
 'BK': 'BNY Mellon',
 'BBWI': 'Bath & Body Works, Inc.',
 'BAX': 'Baxter International',
 'BDX': 'Becton Dickinson',
 'BRK.B': 'Berkshire Hathaway',
 'BBY': 'Best Buy',
 'BIO': 'Bio-Rad Laboratories',
 'TECH': 'Bio-Techne',
 'BIIB': 'Biogen',
 'BLK': 'BlackRock',
 'BX': 'Blackstone Inc.',
 'BA': 'Boeing',
 'BKNG': 'Booking Holdings',
 'BWA': 'BorgWarner',
 'BSX': 'Boston Scientific',
 'BMY': 'Bristol Myers Squibb',
 'AVGO': 'Broadcom',
 'BR': 'Broadridge Financial Solutions',
 'BRO': 'Brown & Brown',
 'BF.B': 'Brown–Forman',
 'BLDR': 'Builders FirstSource',
 'BG': 'Bunge Global',
 'BXP': 'BXP, Inc.',
 'CHRW': 'C.H. Robinson',
 'CDNS': 'Cadence Design Systems',
 'CZR': 'Caesars Entertainment',
 'CPT': 'Camden Property Trust',
 'CPB': 'Campbell Soup Company',
 'COF': 'Capital One',
 'CAH': 'Cardinal Health',
 'KMX': 'CarMax',
 'CCL': 'Carnival',
 'CARR': 'Carrier Global',
 'CTLT': 'Catalent',
 'CAT': 'Caterpillar Inc.',
 'CBOE': 'Cboe Global Markets',
 'CBRE': 'CBRE Group',
 'CDW': 'CDW',
 'CE': 'Celanese',
 'COR': 'Cencora',
 'CNC': 'Centene Corporation',
 'CNP': 'CenterPoint Energy',
 'CF': 'CF Industries',
 'CRL': 'Charles River Laboratories',
 'SCHW': 'Charles Schwab Corporation',
 'CHTR': 'Charter Communications',
 'CVX': 'Chevron Corporation',
 'CMG': 'Chipotle Mexican Grill',
 'CB': 'Chubb Limited',
 'CHD': 'Church & Dwight',
 'CI': 'Cigna',
 'CINF': 'Cincinnati Financial',
 'CTAS': 'Cintas',
 'CSCO': 'Cisco',
 'C': 'Citigroup',
 'CFG': 'Citizens Financial Group',
 'CLX': 'Clorox',
 'CME': 'CME Group',
 'CMS': 'CMS Energy',
 'KO': 'Coca-Cola Company (The)',
 'CTSH': 'Cognizant',
 'CL': 'Colgate-Palmolive',
 'CMCSA': 'Comcast',
 'CAG': 'Conagra Brands',
 'COP': 'ConocoPhillips',
 'ED': 'Consolidated Edison',
 'STZ': 'Constellation Brands',
 'CEG': 'Constellation Energy',
 'COO': 'The Cooper Companies, Inc',
 'CPRT': 'Copart',
 'GLW': 'Corning Inc.',
 'CPAY': 'Corpay',
 'CTVA': 'Corteva',
 'CSGP': 'CoStar Group',
 'COST': 'Costco',
 'CTRA': 'Coterra',
 'CRWD': 'CrowdStrike',
 'CCI': 'Crown Castle',
 'CSX': 'CSX Corporation',
 'CMI': 'Cummins',
 'CVS': 'CVS Health',
 'DHR': 'Danaher Corporation',
 'DRI': 'Darden Restaurants',
 'DVA': 'DaVita',
 'DAY': 'Dayforce',
 'DECK': 'Deckers Brands',
 'DE': 'Deere & Company',
 'DAL': 'Delta Air Lines',
 'DVN': 'Devon Energy',
 'DXCM': 'Dexcom',
 'FANG': 'Diamondback Energy',
 'DLR': 'Digital Realty',
 'DFS': 'Discover Financial',
 'DG': 'Dollar General',
 'DLTR': 'Dollar Tree',
 'D': 'Dominion Energy',
 'DPZ': "Domino's",
 'DOV': 'Dover Corporation',
 'DOW': 'Dow Inc.',
 'DHI': 'DR Horton',
 'DTE': 'DTE Energy',
 'DUK': 'Duke Energy',
 'DD': 'DuPont',
 'EMN': 'Eastman Chemical Company',
 'ETN': 'Eaton Corporation',
 'EBAY': 'eBay',
 'ECL': 'Ecolab',
 'EIX': 'Edison International',
 'EW': 'Edwards Lifesciences',
 'EA': 'Electronic Arts',
 'ELV': 'Elevance Health',
 'EMR': 'Emerson Electric',
 'ENPH': 'Enphase',
 'ETR': 'Entergy',
 'EOG': 'EOG Resources',
 'EPAM': 'EPAM Systems',
 'EQT': 'EQT Corporation',
 'EFX': 'Equifax',
 'EQIX': 'Equinix',
 'EQR': 'Equity Residential',
 'ESS': 'Essex Property Trust',
 'EL': 'The Estée Lauder Companies Inc',
 'ETSY': 'Etsy',
 'EG': 'Everest Group',
 'EVRG': 'Evergy',
 'ES': 'Eversource',
 'EXC': 'Exelon',
 'EXPE': 'Expedia Group',
 'EXPD': 'Expeditors International',
 'EXR': 'Extra Space Storage',
 'XOM': 'ExxonMobil',
 'FFIV': 'F5, Inc.',
 'FDS': 'FactSet',
 'FICO': 'Fair Isaac',
 'FAST': 'Fastenal',
 'FRT': 'Federal Realty',
 'FDX': 'FedEx',
 'FIS': 'Fidelity National Information Services',
 'FITB': 'Fifth Third Bank',
 'FSLR': 'First Solar',
 'FE': 'FirstEnergy',
 'FI': 'Fiserv',
 'FMC': 'FMC Corporation',
 'F': 'Ford Motor Company',
 'FTNT': 'Fortinet',
 'FTV': 'Fortive',
 'FOXA': 'Fox Corporation (Class A)',
 'FOX': 'Fox Corporation (Class B)',
 'BEN': 'Franklin Templeton',
 'FCX': 'Freeport-McMoRan',
 'GRMN': 'Garmin',
 'IT': 'Gartner',
 'GE': 'GE Aerospace',
 'GEHC': 'GE HealthCare',
 'GEV': 'GE Vernova',
 'GEN': 'Gen Digital',
 'GNRC': 'Generac',
 'GD': 'General Dynamics',
 'GIS': 'General Mills',
 'GM': 'General Motors',
 'GPC': 'Genuine Parts Company',
 'GILD': 'Gilead Sciences',
 'GPN': 'Global Payments',
 'GL': 'Globe Life',
 'GDDY': 'GoDaddy',
 'GS': 'Goldman Sachs',
 'HAL': 'Halliburton',
 'HIG': 'The Hartford Financial Services Group, Inc',
 'HAS': 'Hasbro',
 'HCA': 'HCA Healthcare',
 'DOC': 'Healthpeak Properties',
 'HSIC': 'Henry Schein',
 'HSY': 'The Hershey Company',
 'HES': 'Hess Corporation',
 'HPE': 'Hewlett Packard Enterprise',
 'HLT': 'Hilton Worldwide',
 'HOLX': 'Hologic',
 'HD': 'The Home Depot, Inc',
 'HON': 'Honeywell',
 'HRL': 'Hormel Foods',
 'HST': 'Host Hotels & Resorts',
 'HWM': 'Howmet Aerospace',
 'HPQ': 'HP Inc.',
 'HUBB': 'Hubbell Incorporated',
 'HUM': 'Humana',
 'HBAN': 'Huntington Bancshares',
 'HII': 'Huntington Ingalls Industries',
 'IBM': 'IBM',
 'IEX': 'IDEX Corporation',
 'IDXX': 'Idexx Laboratories',
 'ITW': 'Illinois Tool Works',
 'INCY': 'Incyte',
 'IR': 'Ingersoll Rand',
 'PODD': 'Insulet Corporation',
 'INTC': 'Intel',
 'ICE': 'Intercontinental Exchange',
 'IFF': 'International Flavors & Fragrances',
 'IP': 'International Paper',
 'IPG': 'The Interpublic Group of Companies, Inc',
 'INTU': 'Intuit',
 'ISRG': 'Intuitive Surgical',
 'IVZ': 'Invesco',
 'INVH': 'Invitation Homes',
 'IQV': 'IQVIA',
 'IRM': 'Iron Mountain',
 'JBHT': 'J.B. Hunt',
 'JBL': 'Jabil',
 'JKHY': 'Jack Henry & Associates',
 'J': 'Jacobs Solutions',
 'JNJ': 'Johnson & Johnson',
 'JCI': 'Johnson Controls',
 'JPM': 'JPMorgan Chase',
 'JNPR': 'Juniper Networks',
 'K': 'Kellanova',
 'KVUE': 'Kenvue',
 'KDP': 'Keurig Dr Pepper',
 'KEY': 'KeyCorp',
 'KEYS': 'Keysight',
 'KMB': 'Kimberly-Clark',
 'KIM': 'Kimco Realty',
 'KMI': 'Kinder Morgan',
 'KKR': 'KKR',
 'KLAC': 'KLA Corporation',
 'KHC': 'Kraft Heinz',
 'KR': 'Kroger',
 'LHX': 'L3Harris',
 'LH': 'LabCorp',
 'LRCX': 'Lam Research',
 'LW': 'Lamb Weston',
 'LVS': 'Las Vegas Sands',
 'LDOS': 'Leidos',
 'LEN': 'Lennar',
 'LLY': 'Lilly (Eli)',
 'LIN': 'Linde plc',
 'LYV': 'Live Nation Entertainment',
 'LKQ': 'LKQ Corporation',
 'LMT': 'Lockheed Martin',
 'L': 'Loews Corporation',
 'LOW': "Lowe's",
 'LULU': 'Lululemon Athletica',
 'LYB': 'LyondellBasell',
 'MTB': 'M&T Bank',
 'MRO': 'Marathon Oil',
 'MPC': 'Marathon Petroleum',
 'MKTX': 'MarketAxess',
 'MAR': 'Marriott International',
 'MMC': 'Marsh McLennan',
 'MLM': 'Martin Marietta Materials',
 'MAS': 'Masco',
 'MA': 'Mastercard',
 'MTCH': 'Match Group',
 'MKC': 'McCormick & Company',
 'MCD': "McDonald's",
 'MCK': 'McKesson Corporation',
 'MDT': 'Medtronic',
 'MRK': 'Merck & Co.',
 'META': 'Meta Platforms',
 'MET': 'MetLife',
 'MTD': 'Mettler Toledo',
 'MGM': 'MGM Resorts',
 'MCHP': 'Microchip Technology',
 'MU': 'Micron Technology',
 'MSFT': 'Microsoft',
 'MAA': 'Mid-America Apartment Communities',
 'MRNA': 'Moderna',
 'MHK': 'Mohawk Industries',
 'MOH': 'Molina Healthcare',
 'TAP': 'Molson Coors Beverage Company',
 'MDLZ': 'Mondelez International',
 'MPWR': 'Monolithic Power Systems',
 'MNST': 'Monster Beverage',
 'MCO': "Moody's Corporation",
 'MS': 'Morgan Stanley',
 'MOS': 'The Mosaic Company',
 'MSI': 'Motorola Solutions',
 'MSCI': 'MSCI',
 'NDAQ': 'Nasdaq, Inc.',
 'NTAP': 'NetApp',
 'NFLX': 'Netflix',
 'NEM': 'Newmont',
 'NWSA': 'News Corp (Class A)',
 'NWS': 'News Corp (Class B)',
 'NEE': 'NextEra Energy',
 'NKE': 'Nike, Inc.',
 'NI': 'NiSource',
 'NDSN': 'Nordson Corporation',
 'NSC': 'Norfolk Southern Railway',
 'NTRS': 'Northern Trust',
 'NOC': 'Northrop Grumman',
 'NCLH': 'Norwegian Cruise Line Holdings',
 'NRG': 'NRG Energy',
 'NUE': 'Nucor',
 'NVDA': 'Nvidia',
 'NVR': 'NVR, Inc.',
 'NXPI': 'NXP Semiconductors',
 'ORLY': "O'Reilly Auto Parts",
 'OXY': 'Occidental Petroleum',
 'ODFL': 'Old Dominion',
 'OMC': 'Omnicom Group',
 'ON': 'ON Semiconductor',
 'OKE': 'ONEOK',
 'ORCL': 'Oracle Corporation',
 'OTIS': 'Otis Worldwide',
 'PCAR': 'Paccar',
 'PKG': 'Packaging Corporation of America',
 'PANW': 'Palo Alto Networks',
 'PARA': 'Paramount Global',
 'PH': 'Parker Hannifin',
 'PAYX': 'Paychex',
 'PAYC': 'Paycom',
 'PYPL': 'PayPal',
 'PNR': 'Pentair',
 'PEP': 'PepsiCo',
 'PFE': 'Pfizer',
 'PCG': 'PG&E Corporation',
 'PM': 'Philip Morris International',
 'PSX': 'Phillips 66',
 'PNW': 'Pinnacle West',
 'PNC': 'PNC Financial Services',
 'POOL': 'Pool Corporation',
 'PPG': 'PPG Industries',
 'PPL': 'PPL Corporation',
 'PFG': 'Principal Financial Group',
 'PG': 'Procter & Gamble',
 'PGR': 'Progressive Corporation',
 'PLD': 'Prologis',
 'PRU': 'Prudential Financial',
 'PEG': 'Public Service Enterprise Group',
 'PTC': 'PTC',
 'PSA': 'Public Storage',
 'PHM': 'PulteGroup',
 'QRVO': 'Qorvo',
 'PWR': 'Quanta Services',
 'QCOM': 'Qualcomm',
 'DGX': 'Quest Diagnostics',
 'RL': 'Ralph Lauren Corporation',
 'RJF': 'Raymond James',
 'RTX': 'RTX Corporation',
 'O': 'Realty Income',
 'REG': 'Regency Centers',
 'REGN': 'Regeneron',
 'RF': 'Regions Financial Corporation',
 'RSG': 'Republic Services',
 'RMD': 'ResMed',
 'RVTY': 'Revvity',
 'ROK': 'Rockwell Automation',
 'ROL': 'Rollins, Inc.',
 'ROP': 'Roper Technologies',
 'ROST': 'Ross Stores',
 'RCL': 'Royal Caribbean Group',
 'SPGI': 'S&P Global',
 'CRM': 'Salesforce',
 'SBAC': 'SBA Communications',
 'SLB': 'Schlumberger',
 'STX': 'Seagate Technology',
 'SRE': 'Sempra',
 'NOW': 'ServiceNow',
 'SHW': 'Sherwin-Williams',
 'SPG': 'Simon Property Group',
 'SWKS': 'Skyworks Solutions',
 'SJM': 'The J. M. Smucker Company',
 'SW': 'Smurfit WestRock',
 'SNA': 'Snap-on',
 'SOLV': 'Solventum',
 'SO': 'Southern Company',
 'LUV': 'Southwest Airlines',
 'SWK': 'Stanley Black & Decker',
 'SBUX': 'Starbucks',
 'STT': 'State Street Corporation',
 'STLD': 'Steel Dynamics',
 'STE': 'Steris',
 'SYK': 'Stryker Corporation',
 'SMCI': 'Supermicro',
 'SYF': 'Synchrony Financial',
 'SNPS': 'Synopsys',
 'SYY': 'Sysco',
 'TMUS': 'T-Mobile US',
 'TROW': 'T. Rowe Price',
 'TTWO': 'Take-Two Interactive',
 'TPR': 'Tapestry, Inc.',
 'TRGP': 'Targa Resources',
 'TGT': 'Target Corporation',
 'TEL': 'TE Connectivity',
 'TDY': 'Teledyne Technologies',
 'TFX': 'Teleflex',
 'TER': 'Teradyne',
 'TSLA': 'Tesla, Inc.',
 'TXN': 'Texas Instruments',
 'TXT': 'Textron',
 'TMO': 'Thermo Fisher Scientific',
 'TJX': 'TJX Companies',
 'TSCO': 'Tractor Supply',
 'TT': 'Trane Technologies',
 'TDG': 'TransDigm Group',
 'TRV': 'Travelers Companies Inc',
 'TRMB': 'Trimble Inc.',
 'TFC': 'Truist',
 'TYL': 'Tyler Technologies',
 'TSN': 'Tyson Foods',
 'USB': 'U.S. Bank',
 'UBER': 'Uber',
 'UDR': 'UDR, Inc.',
 'ULTA': 'Ulta Beauty',
 'UNP': 'Union Pacific Corporation',
 'UAL': 'United Airlines Holdings',
 'UPS': 'United Parcel Service',
 'URI': 'United Rentals',
 'UNH': 'UnitedHealth Group',
 'UHS': 'Universal Health Services',
 'VLO': 'Valero Energy',
 'VTR': 'Ventas',
 'VLTO': 'Veralto',
 'VRSN': 'Verisign',
 'VRSK': 'Verisk',
 'VZ': 'Verizon',
 'VRTX': 'Vertex Pharmaceuticals',
 'VTRS': 'Viatris',
 'VICI': 'Vici Properties',
 'V': 'Visa Inc.',
 'VST': 'Vistra',
 'VMC': 'Vulcan Materials Company',
 'WRB': 'W. R. Berkley Corporation',
 'GWW': 'W. W. Grainger',
 'WAB': 'Wabtec',
 'WBA': 'Walgreens Boots Alliance',
 'WMT': 'Walmart',
 'DIS': 'Walt Disney Co',
 'WBD': 'Warner Bros. Discovery',
 'WM': 'Waste Management',
 'WAT': 'Waters Corporation',
 'WEC': 'WEC Energy Group',
 'WFC': 'Wells Fargo',
 'WELL': 'Welltower',
 'WST': 'West Pharmaceutical Services',
 'WDC': 'Western Digital',
 'WY': 'Weyerhaeuser',
 'WMB': 'Williams Companies',
 'WTW': 'Willis Towers Watson',
 'WYNN': 'Wynn Resorts',
 'XEL': 'Xcel Energy',
 'XYL': 'Xylem Inc.',
 'YUM': 'Yum! Brands',
 'ZBRA': 'Zebra Technologies',
 'ZBH': 'Zimmer Biomet',
 'ZTS': 'Zoetis',
 'WDAY': 'Workday Inc',
 'APO': 'Apollo Global Management',
 'LII': 'Lennox International'}


def parse_arguments():
    parser = argparse.ArgumentParser(description='Update stock data with configurable time delta')
    parser.add_argument('--time_delta', type=float, default=1.2,
                      help='Time delta in hours (default: 1.2)')
    return parser.parse_args()

def get_updated_stock_data(symbols):
    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    print(f"Getting the symbols from Alpaca Markets...")
    request_parameters = StockBarsRequest(
                    symbol_or_symbols=symbols,
                    timeframe=TimeFrame(1, TimeFrameUnit.Minute),
                    start=pd.to_datetime(start_date).tz_convert('America/New_York'),\
                    adjustment = "all",
                    )
    df = data_client.get_stock_bars(request_parameters).df.reset_index()

    return df

def save_updated_stock_data(df):
    start_time = time.time()

    all_symbols = list(symbols_names.keys())
    need_to_update_symbols = df.reset_index()["symbol"].unique() if len(df) > 0 else []
    no_need_to_update_symbols =[symbol for symbol in all_symbols if symbol not in need_to_update_symbols]

    print(f"No need to update {len(no_need_to_update_symbols)} symbols")


    # CSV files that need to be updated
    if len(need_to_update_symbols) > 0:
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
        # Touch the file if no need to update
        for file in os.listdir(DATA_PATH):
            if file.endswith('.csv') or file.endswith('.CSV'):
                symbol = file.split('.')[0]
                if symbol in no_need_to_update_symbols:
                    os.utime(os.path.join(DATA_PATH, file), None)

        consolidated_file_name = next(f for f in os.listdir(DATA_PATH) if f.endswith('.CSV'))
        os.utime(os.path.join(DATA_PATH, consolidated_file_name), None)


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

    all_spy_symbols = sorted(list(symbols_names.keys()), reverse=True)
    current_spy_symbols = [f.split('.')[0] for f in os.listdir(DATA_PATH) if f.split('.')[0] in all_spy_symbols]
    print(current_spy_symbols)
    df = get_updated_stock_data(current_spy_symbols)
    save_updated_stock_data(df)

if __name__ == "__main__":
    main()
