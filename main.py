from flask import Flask, render_template, jsonify, request, send_file
import os
from datetime import datetime

#HOST = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
#PORT = os.getenv('PORT', 8080)

app = Flask(__name__)

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    if size_bytes >= 1024 * 1024 * 1024:  # 1 GB or larger
        size_gb = round(size_bytes / (1024 * 1024 * 1024), 2)
        return f"{size_gb} GB"
    else:
        size_mb = round(size_bytes / (1024 * 1024), 2)
        return f"{size_mb} MB"


def get_tickers(search_query=None):
    data_dir = './data'
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    files.append("503 S&P Symbols - All data.CSV")
    tickers = []
    for file in files:
        file_path = os.path.join(data_dir, file)
        modified_time = os.path.getmtime(file_path)
        time_delta = datetime.now() - datetime.fromtimestamp(modified_time)
        hours_ago = time_delta.total_seconds() / 3600
        minutes_ago = (time_delta.total_seconds() % 3600) / 60

        parts = os.path.splitext(file)[0].split('_')
        ticker = parts[0]


        if search_query is None or search_query.lower() in ticker.lower():
            tickers.append({
                'ticker': ticker,
                'hours_ago': int(hours_ago),
                'minutes_ago': int(minutes_ago),
                'file_size': get_file_size(file_path),
            })

    tickers.sort(key=lambda x: x['ticker'])

    return tickers

@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('search', '')
    try:
        all_tickers = get_tickers(search_query)
        if all_tickers is None:
            all_tickers = []
    except Exception as e:
        print(f"Error fetching tickers: {e}")
        all_tickers = []

    displayed_tickers = all_tickers[:7]
    has_more = len(all_tickers) > 7
    return render_template(
        'index.html',
        tickers=displayed_tickers,
        search_query=search_query,
        has_more=has_more,
        )

@app.route('/download/<path:filename>')
def download_file(filename):
    file_path = os.path.join('./data', filename)
    if os.path.exists(file_path) and filename.lower().endswith('.csv'):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found or invalid file format", 404



@app.route('/api/symbols_info')
def api_tickers():
    return jsonify(get_tickers())


if __name__ == '__main__':
    app.run()
