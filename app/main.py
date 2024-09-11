from flask import Flask, render_template, request, send_from_directory, abort
from urllib.parse import unquote
import os
from datetime import datetime

app = Flask(__name__,
       static_folder='./storage')

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    if size_bytes >= 1024 * 1024 * 1024:  # 1 GB or larger in GB
        size_gb = round(size_bytes / (1024 * 1024 * 1024), 2)
        return f"{size_gb} GB"
    else:
        size_mb = round(size_bytes / (1024 * 1024), 2)
        return f"{size_mb} MB"

def get_symbols(search_query=None):
    data_dir = os.path.join(os.path.dirname(__file__), 'storage')
    files = [f for f in os.listdir(data_dir) if (f.endswith('.csv') or f.endswith('.CSV'))]

    symbols = []
    for file in files:
        file_path = os.path.join(data_dir, file)
        modified_time = os.path.getmtime(file_path)
        time_delta = datetime.now() - datetime.fromtimestamp(modified_time)
        hours_ago = time_delta.total_seconds() / 3600
        minutes_ago = (time_delta.total_seconds() % 3600) / 60

        symbol = os.path.splitext(file)[0]

        if search_query is None or search_query.lower() in symbol.lower():
            symbols.append({
                'symbol': symbol,
                'hours_ago': int(hours_ago),
                'minutes_ago': int(minutes_ago),
                'file_size': get_file_size(file_path),
            })

    symbols.sort(key=lambda x: (len(x['symbol']) <= 5, x['symbol']))

    return symbols

@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    try:
        all_symbols = get_symbols(search_query)
        if all_symbols is None:
            all_symbols = []
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        all_symbols = []

    displayed_symbols = all_symbols[:7]
    has_more = len(all_symbols) > 7

    return render_template(
        'index.html',
        symbols=displayed_symbols,
        search_query=search_query,
        has_more=has_more,
        )

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    data_dir = os.path.join(os.path.dirname(__file__), 'storage')
    decoded_filename = unquote(filename).lower()

    for file in os.listdir(data_dir):
        if file.lower() == decoded_filename:
            return send_from_directory(
                directory=data_dir,
                path=file,
                as_attachment=True,
                max_age=0
            )

    abort(404, description="File not found or invalid file format")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
