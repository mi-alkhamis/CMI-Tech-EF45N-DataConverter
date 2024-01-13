from datetime import datetime
import sqlite3
import os

# ------------------------------  Configuration  ------------------------------
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
# ------------------------------  READ DB Files  ------------------------------


def walk(db_path):
    """
    Read All DB files in path and return DB file and DeviceID

    Args:
        db_path (str): The path to the directory containing the DB files.
    """
    for dir_path, _, filenames in os.walk(db_path):
        if not filenames:
            continue
        if "ServiceLog.db" not in filenames:
            print(f"'ServiceLog.db' not found in '{dir_path}'.")
            continue
        db_path = os.path.join(dir_path, "ServiceLog.db")
        # normilize path and split it and put device folder name in device_num
        device_num = os.path.normpath(db_path).split(os.sep)[1]
        read_db(db_path, DEVICE_ID.get(device_num))


def read_db(db_path, deviceID):
    """
    Connect DB and run query to filter proper data.

    Args:
        db_path (str): The path to the DB file.
        deviceID (str): The device ID associated with the DB file.
    """
    connection = sqlite3.connect(db_path)
    query = f"""
                SELECT Timestamp,UserUID from  event_log
                WHERE EventType = "Recognition"
                AND AdditionalData = "Allowed"
				order by Timestamp
            """
    cursor = connection.cursor()
    cursor.execute(query)
    create_txt_file(cursor.fetchall(), deviceID)
# ------------------------------  Convert  ------------------------------


def create_txt_file(raw_data, deviceID):
    """Convert CMI-TECH EF-45 Enterance Log to RAYA  format
    3120110223160100010000000301000118
    31 2011-02-23 16:01 0001 0000000301 0001 18
    31 date time Enter_type userID device_ID 18

    Args:
        raw_data (list): A list of tuples containing the timestamp and user UID from the DB query.
        deviceID (str): The device ID associated with the DB file.
    """
    if not os.path.exists(EXPORT_PATH):
        os.mkdir(EXPORT_PATH)
    export_file = f"{EXPORT_PATH}\{deviceID}.txt"
    with open(export_file, "w") as file:
        # Use list comprehensions to create lists from existing iterables
        for row in raw_data:
            userID = row[1].strip().zfill(10)
            timestamp = convert_timestamp(row[0])
            log_sequence = f"31{timestamp}0003{userID}{deviceID}18"
            file.write(log_sequence)
            file.write("\n")


def convert_timestamp(timestamp):
    """Convert CMI-TECH EF-45 Enterance Log Time format(2023-02-15T13:08:19Z)
    to RAYA  format(202302151308).

    Args:
        timestamp (str): The timestamp in CMI-TECH EF-45 Enterance Log Time format.

    Returns:
        str: The timestamp in RAYA format.
    """

    dt_object = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    return dt_object.strftime("%Y%m%d%H%M")


# ------------------------------  MAIN  ------------------------------
walk(DB_PATH)
