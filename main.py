import os
import sqlite3
import sys
import logging
from datetime import date, datetime
from pathlib import Path
from shutil import rmtree

DEVICE_ID = {
    "150": "8242",
    "151": "9608",
    "152": "8984",
    "153": "9317",
    "154": "9319",
    "155": "9318",
    "156": "8983",
    "157": "8965",
    "158": "8040",
    "159": "9313",
    "160": "7268",
    "161": "8992",
    "162": "9000",
    "163": "8969",
    "164": "8997",
    "165": "8966",
    "144": "7904",
    "2963":"2963",
    "3225": "9577",
    "3425":"7792"
}
DB_PATH = "cmitech"
TXT_EXPORT_PATH = os.path.join("export", "txt")
CSV_EXPORT_PATH = os.path.join("export", "csv")
DB_FILENAME = "ServiceLog.db"

logging.basicConfig(level=logging.INFO)


def walk(db_path, start_date, end_date):
    for dir_path, _, filenames in os.walk(db_path):
        if not filenames:
            continue
        if DB_FILENAME not in filenames:
            logging.warning(f"{DB_FILENAME} not found in '{dir_path}'.")
            continue
        db_file_path = os.path.join(dir_path, DB_FILENAME)
        device_serial = os.path.normpath(db_file_path).split(os.sep)[1]
        device_id = DEVICE_ID.get(device_serial)
        if device_id:
            read_db(db_file_path, device_id, start_date, end_date)
        else:
            logging.warning(f"No device ID found for serial '{device_serial}'.")


def read_db(db_path, device_id, start_date, end_date):
    event_type = "Recognition"
    additional_data = "Allowed"
    query = """
                SELECT Timestamp, UserUID
                FROM  event_log
                WHERE EventType = ?
                AND AdditionalData = ?
                AND substr(Timestamp,1,10) >= ?
                AND substr(Timestamp,1,10) <= ?
				ORDER BY  Timestamp
            """
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(query, (event_type, additional_data, start_date, end_date))
            data = cursor.fetchall()
            if data:
                create_txt_file(data, device_id)
                create_csv_file(data, device_id)
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def create_txt_file(raw_data, device_id):
    """
        Convert log data to RAYA format and write to a text file.
        3120110223160100010000000301000118
        31 2011-02-23 16:01 0003 0000000301 0001 18
        31 date time Enter_type userID device_ID 18
    """
    prefix = "31"
    suffix = "18"
    enterance_type = "0003"
    os.makedirs(TXT_EXPORT_PATH, exist_ok=True)
    export_file = os.path.join(TXT_EXPORT_PATH, f"{device_id}.txt")
    try:
        with open(export_file, "w") as file:
            for row in raw_data:
                userID = row[1].strip().zfill(10)
                timestamp = convert_timestamp(row[0])
                log_sequence = (
                    f"{prefix}{timestamp}{enterance_type}{userID}{device_id}{suffix}"
                )
                file.write(f"{log_sequence}\n")
    except OSError as e:
        logging.error(f"File error: {e}")
    logging.info(f"File '{export_file}' was created successfully.")


def create_csv_file(raw_data, device_id):
    enterance_type = "0003"
    csv_file_path = Path(CSV_EXPORT_PATH).joinpath('export-amirkabir.csv')
    if not os.path.exists(CSV_EXPORT_PATH):
        os.makedirs(CSV_EXPORT_PATH)
    export_file = os.path.join(CSV_EXPORT_PATH, f"export-amirkabir.csv")
    try:
        with open(export_file, "a+") as file:
            for row in raw_data:
                userID = row[1].strip()
                date, time = split_timestamp(row[0])
                log_sequence = f"{userID},{date},{time},{enterance_type},{device_id}"
                file.write(f"{log_sequence}\n")
    except OSError as e:
        logging.error(f"File error: {e}")
    logging.info(f"File '{export_file}' was created successfully.")


def split_timestamp(timestamp):
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    date = timestamp.strftime("%Y-%m-%d")
    time = timestamp.strftime("%H:%M")
    return date, time


def convert_timestamp(timestamp):
    """
        convert Log Time format(2023-02-15T13:08:19Z) to (202302151308).
    """
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return timestamp.strftime("%Y%m%d%H%M")
def main():
    timestamp = input("Enter start date in YYYY-MM-DD format:\n")
    try:
        start_date = datetime.strptime(timestamp, "%Y-%m-%d").date()
    except ValueError as e:
        logging.error(
            f"Error: Invalid date format. Please enter the date in YYYY-MM-DD format. {e}"
        )
        sys.exit(1)
    timestamp = input("Enter end date in YYYY-MM-DD format:\n")
    try:
        end_date = datetime.strptime(timestamp, "%Y-%m-%d").date()
    except ValueError as e:
        logging.error(
            f"Error: Invalid date format. Please enter the date in YYYY-MM-DD format. {e}"
        )
        sys.exit(1)
    try:
        rmtree('export')
    except:
        logging.error(f'Unable to delete file. {e}')
    walk(DB_PATH, start_date,end_date)

if __name__ == "__main__":
    main()
