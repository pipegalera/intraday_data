from flask import Flask, render_template, jsonify, request, send_file
import os
from datetime import datetime

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
    files = [f for f in os.listdir(data_dir) if f.endswith('.parquet')]
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
    all_tickers = get_tickers(search_query)
    displayed_tickers = all_tickers[:7]  # Only take the first 10
    has_more = len(all_tickers) > 7  # Check if there are more than 10 results
    return render_template(
        'index.html',
        tickers=displayed_tickers,
        search_query=search_query,
        has_more=has_more,
        )

@app.route('/download/<ticker>')
def download_file(ticker):
    file_path = os.path.join('./data', f'{ticker}.parquet')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/api/symbols_info')
def api_tickers():
    return jsonify(get_tickers())


if __name__ == '__main__':
    app.run(debug=True)
