from flask import Flask, Response, render_template, request, send_from_directory, abort, jsonify, url_for
from urllib.parse import unquote
from datetime import datetime, timedelta
import os
import re
import json

symbols_names = json.load(open("app/sp500_symbols.json"))

app = Flask(__name__, static_folder='static')

def get_next_hour():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return (next_hour - now).total_seconds()

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    if size_bytes >= 1024 * 1024 * 1024:  # 1 GB or larger in GB
        size_gb = round(size_bytes / (1024 * 1024 * 1024), 2)
        return f"{size_gb} GB"
    else:
        size_mb = round(size_bytes / (1024 * 1024), 2)
        return f"{size_mb} MB"

def file_exists(file_path):
    return os.path.exists(file_path)

def get_symbols(search_query=None):
    data_dir = os.path.join(os.path.dirname(__file__), 'storage')
    files = [f for f in os.listdir(data_dir) if
        (f.lower().endswith('.csv')) and
        '_' not in f
    ]
    symbols = []
    for file in files:
            file_path = os.path.join(data_dir, file)
            modified_time = os.path.getmtime(file_path)
            time_delta = datetime.now() - datetime.fromtimestamp(modified_time)
            hours_ago = time_delta.total_seconds() / 3600
            minutes_ago = (time_delta.total_seconds() % 3600) / 60

            symbol = os.path.splitext(file)[0]
            symbol_name = symbols_names.get(symbol, "")

            if (search_query is None or
                search_query.lower() in symbol.lower() or
                search_query.lower() in symbol_name.lower()):
                symbols.append({
                    'symbol': symbol,
                    'name': symbols_names.get(symbol),
                    'hours_ago': int(hours_ago),
                    'minutes_ago': int(minutes_ago),
                    'file_size': get_file_size(file_path),
                    'file_path': file_path,
                    'modified_time': modified_time,
                    'download_url': file,
                    'file_available': file_exists(file_path),
                })

    symbols.sort(key=lambda x: (len(x['symbol']) <= 5, x['symbol']))

    return symbols

@app.route('/symbols-info')
def check_file_sizes():
    symbols = get_symbols()
    return jsonify([{
        'symbol': s['symbol'],
        'name': s['name'],
        'hours_ago': s['hours_ago'],
        'minutes_ago': s['minutes_ago'],
        'file_size': s['file_size']
    } for s in symbols])


def file_list():
    data_dir = os.path.join(os.path.dirname(__file__), 'storage')
    files = [f for f in os.listdir(data_dir) if
        (f.lower().endswith('.csv')) and
        '_' not in f
    ]
    file_urls = [f'/downloads/{file}' for file in files]
    return render_template('file_list.html', file_urls=file_urls)

# Fallback download
# @app.route('/downloads/<path:filename>')
# def download_file(filename):
#     storage_dir = os.path.join(os.path.dirname(__file__), 'storage')
#     return send_from_directory(storage_dir, filename, as_attachment=True)


@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    try:
        all_symbols = get_symbols(search_query)
        if all_symbols is None:
            all_symbols = []
            for symbol in all_symbols:
                symbol['download_url'] = url_for('download_file',
                    filename=symbol['filename'], _external=True)

    except Exception as e:
        print(f"Error fetching symbols: {e}")
        all_symbols = []

    seconds_to_next_hour = get_next_hour()

    # Return Google Analytics
    GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID")

    return render_template(
        'index.html',
        symbols=all_symbols,
        search_query=search_query,
        seconds_to_next_hour=int(seconds_to_next_hour),
        ga_id=GA_MEASUREMENT_ID,
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
