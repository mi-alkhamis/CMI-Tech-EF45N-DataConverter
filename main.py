from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sqlite3
import os, sys


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
    "1919": "1919",
}
DB_PATH = "cmitech"
EXPORT_PATH = "export"
DB_FILENAME = "ServiceLog.db"


def walk(db_path):
    """
    Read All DB files in path and return DB file and device_id

    Args:
        db_path (str): The path to the directory containing the DB files.
    """
    for dir_path, _, filenames in os.walk(db_path):
        if not filenames:
            continue
        if DB_FILENAME not in filenames:
            print(f"{DB_FILENAME} not found in '{dir_path}'.")
            continue
        db_path = os.path.join(dir_path, DB_FILENAME)
        device_serial = os.path.normpath(db_path).split(os.sep)[1]
        read_db(db_path, DEVICE_ID.get(device_serial), startdate)


def read_db(db_path, device_id, start_date):
    """
    Connect DB and run query to filter proper data.

    Args:
        db_path (str): The path to the DB file.
        device_id (str): The device ID associated with the DB file.
    """
    connection = sqlite3.connect(db_path)
    yesterday = (datetime.now() - relativedelta(days=1)).strftime("%Y-%m-%d")
    event_type = "Recognition"
    additional_data = "Allowed"
    query = f"""
                SELECT Timestamp, UserUID
                FROM  event_log
                WHERE EventType = ?
                AND AdditionalData = ?
                AND Timestamp >= ?
                AND Timestamp <= ?
				ORDER BY  Timestamp
            """
    cursor = connection.cursor()
    cursor.execute(query, (event_type, additional_data, start_date, yesterday))
    create_txt_file(cursor.fetchall(), device_id)


def create_txt_file(raw_data, device_id):
    """Convert CMI-TECH EF-45 Enterance Log to RAYA  format
    3120110223160100010000000301000118
    31 2011-02-23 16:01 0003 0000000301 0001 18
    31 date time Enter_type userID device_ID 18

    Args:
        raw_data (list): A list of tuples containing the timestamp and user UID from the DB query.
        device_id (str): The device ID associated with the DB file.
    """
    prefix = "31"
    suffix = "18"
    enterance_type = "0003"

    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
    export_file = os.path.join(EXPORT_PATH, f"{device_id}.txt")
    with open(export_file, "w") as file:
        for row in raw_data:
            userID = row[1].strip().zfill(10)
            timestamp = convert_timestamp(row[0])
            log_sequence = (
                f"{prefix}{timestamp}{enterance_type}{userID}{device_id}{suffix}"
            )
            file.write(f"{log_sequence}\n")


def convert_timestamp(timestamp):
    """Convert CMI-TECH EF-45 Enterance Log Time format(2023-02-15T13:08:19Z)
    to RAYA  format(202302151308).

    Args:
        timestamp (str): The timestamp in CMI-TECH EF-45 Enterance Log Time format.

    Returns:
        str: The timestamp in RAYA format.
    """

    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return timestamp.strftime("%Y%m%d%H%M")


if __name__ == "__main__":
    timestamp = input("Enter start Date in YYYY-MM-DD format:\n")
    try:
        year, month, day = map(int, timestamp.split("-"))
        startdate = date(year, month, day)

    except Exception as e:
        print("Error: Invalid date format. Please enter the date in YYYY-MM-DD format.")
        sys.exit(1)
    except ValueError as e:
        print(f"Value Error. {e}")
        sys.exit(1)
    walk(DB_PATH)
