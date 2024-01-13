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


# ------------------------------  MAIN  ------------------------------
walk(DB_PATH)
