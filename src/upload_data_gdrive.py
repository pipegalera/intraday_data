from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

from dotenv import load_dotenv
load_dotenv()
import os
import time
from utils import spy_symbols
import socket

DATA_PATH = os.getenv("DATA_PATH")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
FOLDER_ID = "1HBQklHrysMzYLCUc9mVjeznjriO7vu_r"
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def delete_parquet_file(service, file_path, folder_id=FOLDER_ID):
    file_name = os.path.basename(file_path)
    query = f"name='{file_name}' and '{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    for file in files:
        service.files().delete(fileId=file.get('id')).execute()
        print(f"Deleted existing file: {file.get('name')} (ID: {file.get('id')})")

def upload_parquet_file(service, file_path, folder_id=FOLDER_ID, max_retries=3, retry_delay=5):
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True, mimetype='application/octet-stream')

    for attempt in range(max_retries):
        try:
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Created new file: {file_name} (ID: {file.get('id')})")
            return
        except (socket.timeout, HttpError) as e:
            if attempt == max_retries - 1:
                print(f"Failed to upload {file_name} after {max_retries} attempts: {str(e)}")
                raise
            else:
                print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

def main():
    service = get_drive_service()

    start_time = time.time()
    """
    for symbol in spy_symbols:
        file_path = DATA_PATH + f"parquet_files/{symbol}.parquet"
        print(f"Updating: {symbol}...")
        delete_parquet_file(service,
                            file_path,
                            folder_id)
        upload_parquet_file(service,
                            file_path,
                            folder_id)
    """
    file_path = DATA_PATH + f"parquet_files/spy_intraday_1M.parquet"
    delete_parquet_file(service,
                        file_path)
    upload_parquet_file(service,
                        file_path)
    end_time = time.time()
    execution_time = round(end_time - start_time,2)
    print(f"Execution time: {execution_time} seconds")

if __name__ == '__main__':
    main()
