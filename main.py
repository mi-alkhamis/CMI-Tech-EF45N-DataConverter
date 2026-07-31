import argparse
import logging
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from shutil import rmtree
from typing import Dict, List, Tuple
from openpyxl import Workbook

# App name and version
APP_NAME = "CMI-TECH EF45 to RAYA Converter"
__version__ = "2.0.0"


# Configuration constants
DEVICE_ID: Dict[str, str] = {
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
    "2963": "2963",
    "325": "9577",
    "345": "7792",
}
EXPORT_BASE_PATH = Path("export").resolve()
TXT_SUBDIR = "text"
XLSX_SUBDIR = "excel"
XLSX_EXPORT_FILENAME = "export.xlsx"
WORKSHEET_TITLE = "گزارش"
WORKSHEET_HEADERS = ["شماره کارت", "تاریخ", "زمان", "نوع تردد", "کد دستگاه"]
DB_PATH = Path("cmitech")
DB_FILENAME = "ServiceLog.db"
RAYA_PREFIX = "31"
RAYA_SUFFIX = "18"
RAYA_ENTRANCE_TYPE = "0003"
EVENT_TYPE = "Recognition"
DATA_TYPE = "Allowed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def parse_timestamp_value(timestamp: str) -> datetime:
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError(f"Invalid timestamp format '{timestamp}'. Expected YYYY-MM-DDTHH:MM:SSZ") from exc


def split_timestamp(timestamp: str) -> Tuple[str, str]:
    parsed = parse_timestamp_value(timestamp)
    return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M")


def convert_timestamp(timestamp: str) -> str:
    parsed = parse_timestamp_value(timestamp)
    return parsed.strftime("%Y%m%d%H%M")


def get_dated_export_root(base_path: Path) -> Path:
    suffix = datetime.now().strftime("%Y-%m-%d")
    return base_path / suffix


def parse_date_string(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"Invalid date format '{value}'. Use YYYY-MM-DD.") from exc


def confirm_yes_no(prompt: str) -> bool:
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def make_export_paths(export_base: Path, dated: bool) -> Tuple[Path, Path, Path]:
    if dated:
        export_root = get_dated_export_root(export_base)
    else:
        export_root = export_base
    txt_export_path = export_root / TXT_SUBDIR
    xlsx_export_path = export_root / XLSX_SUBDIR
    return export_root, txt_export_path, xlsx_export_path


def clean_export_directory(export_path: Path) -> bool:
    if not export_path.exists():
        logging.info("Export path does not exist: %s", export_path)
        return True
    try:
        logging.info("Deleting export directory: %s", export_path)
        rmtree(export_path)
        logging.info("Export directory deleted successfully")
        return True
    except PermissionError as exc:
        logging.error("Permission denied: %s", exc)
    except OSError as exc:
        logging.error("Cannot delete directory: %s", exc)
    return False


def walk(
    db_path: Path,
    start_date: date,
    end_date: date,
    txt_export_path: Path,
    xlsx_export_path: Path,
) -> None:
    all_records: List[Tuple[str, str, str, str, str]] = []
    if not db_path.exists():
        logging.error("Database root path does not exist: %s", db_path)
        return

    for db_file_path in db_path.rglob(DB_FILENAME):
        device_serial = db_file_path.parent.name
        device_id = DEVICE_ID.get(device_serial)
        if not device_id:
            logging.warning("No device ID found for serial '%s' in %s", device_serial, db_file_path)
            continue

        records = read_db(db_file_path, device_id, start_date, end_date, txt_export_path)
        all_records.extend(records)

    if all_records:
        create_xlsx_file(all_records, xlsx_export_path)
    else:
        logging.info("No records found for XLSX export.")


def read_db(
    db_path: Path,
    device_id: str,
    start_date: date,
    end_date: date,
    txt_export_path: Path,
) -> List[Tuple[str, str, str, str, str]]:
    query = (
        "SELECT Timestamp, UserUID "
        "FROM event_log "
        "WHERE EventType = ? "
        "AND AdditionalData = ? "
        "AND substr(Timestamp,1,10) >= ? "
        "AND substr(Timestamp,1,10) <= ? "
        "ORDER BY Timestamp"
    )
    records: List[Tuple[str, str, str, str, str]] = []

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                query,
                (EVENT_TYPE, DATA_TYPE, start_date.isoformat(), end_date.isoformat()),
            )
            rows = cursor.fetchall()
            if not rows:
                logging.info("No matching records found in %s", db_path)
                return records

            create_txt_file(rows, device_id, txt_export_path)
            for row in rows:
                if len(row) < 2:
                    logging.warning("Skipping invalid row: %s", row)
                    continue
                try:
                    date_part, time_part = split_timestamp(row[0])
                except ValueError as exc:
                    logging.warning("Skipping invalid timestamp '%s': %s", row[0], exc)
                    continue
                records.append((row[1].strip(), date_part, time_part, RAYA_ENTRANCE_TYPE, device_id))
    except sqlite3.Error as exc:
        logging.error("Database error in %s: %s", db_path, exc)
    except Exception as exc:
        logging.error("Unexpected error while reading %s: %s", db_path, exc)
    return records


def create_txt_file(raw_data: List[Tuple[str, str]], device_id: str, txt_export_path: Path) -> None:
    txt_export_path.mkdir(parents=True, exist_ok=True)
    export_file = txt_export_path / f"{device_id}.txt"
    try:
        with export_file.open("w", encoding="utf-8") as file:
            for row in raw_data:
                if len(row) < 2:
                    logging.warning("Skipping invalid row: %s", row)
                    continue
                user_id = row[1].strip().zfill(10)
                try:
                    timestamp = convert_timestamp(row[0])
                except ValueError as exc:
                    logging.warning("Skipping invalid timestamp '%s': %s", row[0], exc)
                    continue
                file.write(f"{RAYA_PREFIX}{timestamp}{RAYA_ENTRANCE_TYPE}{user_id}{device_id}{RAYA_SUFFIX}\n")
        logging.info("Created TXT export: %s", export_file)
    except OSError as exc:
        logging.error("Failed to create TXT file %s: %s", export_file, exc)


def create_xlsx_file(raw_data: List[Tuple[str, str, str, str, str]], xlsx_export_path: Path) -> None:
    if Workbook is None:
        raise ImportError("openpyxl is required to create XLSX exports. Install it with 'pip install openpyxl'.")
    xlsx_export_path.mkdir(parents=True, exist_ok=True)
    export_file = xlsx_export_path / XLSX_EXPORT_FILENAME
    try:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = WORKSHEET_TITLE
        worksheet.append(WORKSHEET_HEADERS)
        for row in raw_data:
            worksheet.append(list(row))
        workbook.save(export_file)
        logging.info("Created XLSX export: %s", export_file)
    except OSError as exc:
        logging.error("Failed to create XLSX file %s: %s", export_file, exc)
    except Exception as exc:
        logging.error("Unexpected error while writing XLSX file %s: %s", export_file, exc)


def get_date_input(prompt: str) -> date:
    while True:
        date_str = input(prompt).strip()
        try:
            return parse_date_string(date_str)
        except ValueError as exc:
            logging.error("%s", exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert CMI-TECH EF45 database logs into RAYA TXT and XLSX exports.")
    parser.add_argument(
        "--db-root",
        default=str(DB_PATH),
        help="Root directory containing device folders with ServiceLog.db.",
    )
    parser.add_argument("--export-base", default=str(EXPORT_BASE_PATH), help="Base export directory.")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="End date in YYYY-MM-DD format.")
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Do not create a date-based export subfolder.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete existing export path if it already exists.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{APP_NAME} {__version__}",
        help="Show the application version and exit.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        start_date = (
            parse_date_string(args.start_date) if args.start_date else get_date_input("Enter start date (YYYY-MM-DD): ")
        )
        end_date = (
            parse_date_string(args.end_date) if args.end_date else get_date_input("Enter end date (YYYY-MM-DD): ")
        )
    except ValueError as exc:
        logging.error("%s", exc)
        sys.exit(1)

    if start_date > end_date:
        logging.error("Start date %s cannot be after end date %s.", start_date, end_date)
        sys.exit(1)

    export_base = Path(args.export_base)
    export_root, txt_export_path, xlsx_export_path = make_export_paths(export_base, not args.no_timestamp)

    if export_root.exists():
        if not args.overwrite:
            logging.info("Export path '%s' already exists.", export_root)
            if not confirm_yes_no("Delete existing export path?"):
                logging.error("Aborted because export path already exists.")
                sys.exit(1)
        if not clean_export_directory(export_root):
            sys.exit(1)

    logging.info("Using export path: %s", export_root)
    walk(Path(args.db_root), start_date, end_date, txt_export_path, xlsx_export_path)


if __name__ == "__main__":
    main()
