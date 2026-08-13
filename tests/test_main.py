from datetime import date, datetime
from pathlib import Path

import pytest

from main import (
    clean_export_directory,
    convert_timestamp,
    create_txt_file,
    create_xlsx_file,
    make_export_paths,
    parse_date_string,
    parse_timestamp_value,
    split_timestamp,
)

# ─── parse_timestamp_value ────────────────────────────────────────────────────


def test_parse_timestamp_value():
    result = parse_timestamp_value("2023-02-15T13:08:00Z")
    assert result == datetime(2023, 2, 15, 13, 8, 0)


def test_parse_timestamp_invalid_format():
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        parse_timestamp_value("15-02-2023 13:08:00")


def test_parse_timestamp_empty_string():
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        parse_timestamp_value("")


def test_parse_timestamp_date_only():
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        parse_timestamp_value("2023-02-15")


def test_parse_timestamp_time_only():
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        parse_timestamp_value("13:08:00")


# ─── split_timestamp ──────────────────────────────────────────────────────────


def test_split_timestamp_returns_date_and_time():
    date_part, time_part = split_timestamp("2023-02-15T13:08:00Z")
    assert date_part == "2023-02-15"
    assert time_part == "13:08"


def test_split_timestamp_midnight():
    date_part, time_part = split_timestamp("2023-02-15T00:00:00Z")
    assert date_part == "2023-02-15"
    assert time_part == "00:00"


def test_split_timestamp_invalid_timestamp():
    with pytest.raises(ValueError):
        split_timestamp("not-a-timestamp")


# ─── convert_timestamp ────────────────────────────────────────────────────────


def test_convert_timestamp_format():
    result = convert_timestamp("2023-12-15T13:45:20Z")
    assert result == "202312151345"


def test_convert_timestamp_length():
    result = convert_timestamp("2023-12-15T13:45:20Z")
    assert len(result) == 12


def test_convert_timestamp_invalid():
    with pytest.raises(ValueError):
        convert_timestamp("bad-input")


# ─── parse_date_string ────────────────────────────────────────────────────────


def test_parse_date_string_valid():
    result = parse_date_string("2023-02-15")
    assert result == date(2023, 2, 15)


def test_parse_date_string_wrong_format():
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date_string("15/02/2023")


def test_parse_date_string_empty():
    with pytest.raises(ValueError):
        parse_date_string("")


def test_parse_date_string_returns_date_not_datetime():
    result = parse_date_string("2023-02-15")
    assert isinstance(result, date)
    assert not isinstance(result, datetime)


# ─── make_export_paths ────────────────────────────────────────────────────────


def test_make_export_paths_no_timestamp():
    base = Path("/tmp/export")
    export_root, txt_path, xlsx_path = make_export_paths(base, dated=False)
    assert export_root == base
    assert txt_path == base / "text"
    assert xlsx_path == base / "excel"


def test_make_export_paths_with_timestamp():
    base = Path("/tmp/export")
    export_root, txt_path, xlsx_path = make_export_paths(base, dated=True)
    today = datetime.now().strftime("%Y-%m-%d")
    assert export_root == base / today
    assert txt_path == base / today / "text"
    assert xlsx_path == base / today / "excel"


# ─── clean_export_directory ───────────────────────────────────────────────────


def test_clean_export_directory_nonexistent(tmp_path):
    fake_path = tmp_path / "does_not_exist"
    result = clean_export_directory(fake_path)
    assert result is True


def test_clean_export_directory_existing(tmp_path):
    folder = tmp_path / "export"
    folder.mkdir()
    (folder / "file.txt").write_text("data")
    result = clean_export_directory(folder)
    assert result is True
    assert not folder.exists()


# ─── create_txt_file ──────────────────────────────────────────────────────────


def test_create_txt_file_creates_files(tmp_path):
    rows = [
        ("2023-02-15T13:08:00Z", "0000000301"),
        ("2023-02-15T13:09:00Z", "0000000302"),
    ]
    count = create_txt_file(rows, "8242", tmp_path)
    assert count == 2
    files = list(tmp_path.glob("8242/*.txt"))
    assert len(files) == 2


def test_create_txt_file_content_format(tmp_path):
    rows = [("2023-02-15T13:08:00Z", "301")]
    create_txt_file(rows, "8242", tmp_path)
    files = list(tmp_path.glob("8242/*.txt"))
    content = files[0].read_text().strip()
    assert content.startswith("31")
    assert content.endswith("18")
    assert "8242" in content


def test_create_txt_file_duplicate_handling(tmp_path):
    rows = [
        ("2023-02-15T13:08:00Z", "0000000301"),
        ("2023-02-15T13:08:00Z", "0000000301"),
    ]
    count = create_txt_file(rows, "8242", tmp_path)
    assert count == 2
    files = list(tmp_path.glob("8242/*.txt"))
    assert len(files) == 2


def test_create_txt_file_invalid_timestamp(tmp_path):
    rows = [("bad-timestamp", "0000000301")]
    count = create_txt_file(rows, "8242", tmp_path)
    assert count == 0


# ─── create_xlsx_file ─────────────────────────────────────────────────────────


def test_create_xlsx_file_creates_file(tmp_path):
    records = [
        ("0000000301", "2023-02-15", "13:08", "0003", "8242"),
    ]
    create_xlsx_file(records, tmp_path)
    assert (tmp_path / "export.xlsx").exists()


def test_create_xlsx_file_multiple_rows(tmp_path):
    records = [
        ("0000000301", "2023-02-15", "13:08", "0003", "8242"),
        ("0000000302", "2023-02-15", "13:09", "0003", "8242"),
        ("0000000303", "2023-02-15", "13:10", "0003", "9608"),
    ]
    create_xlsx_file(records, tmp_path)
    assert (tmp_path / "export.xlsx").exists()
