# CMI-TECH EF45 to RAYA Converter

![CI](https://github.com/mi-alkhamis/CMI-Tech-EF45N-DataConverter/actions/workflows/ci.yml/badge.svg)
![Build](https://github.com/mi-alkhamis/CMI-Tech-EF45N-DataConverter/actions/workflows/build-windows-exe.yml/badge.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

A command-line tool that reads `ServiceLog.db` files from CMI-TECH EF45
access-control devices and produces:

- **TXT files** — per-device RAYA sequence files for attendance import.
- **XLSX workbook** — a single consolidated Excel report with Persian column headers.

---

## Installation

```bash
git clone https://github.com/mi-alkhamis/CMI-Tech-EF45N-DataConverter.git
cd CMI-Tech-EF45N-DataConverter

python3 -m venv venv
source venv/bin/activate       # macOS / Linux
venv\Scripts\activate          # Windows

pip install -r requirements.txt
```

## Usage

Run with no arguments for fully interactive mode:

```bash
python main.py
```

Or pass options directly to skip prompts:

```bash
python main.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD [OPTIONS]
```

### Options

| Option | Default | Description |
|---|---|---|
| `--start-date YYYY-MM-DD` | interactive | Start of the date range |
| `--end-date YYYY-MM-DD` | interactive | End of the date range |
| `--db-root PATH` | `cmitech` | Root directory containing device folders |
| `--export-base PATH` | `export` | Base output directory |
| `--user-id USERID` | — | Filter export to only this user ID |
| `--no-timestamp` | off | Disable date-based output subfolder |
| `--overwrite` | off | Delete existing export directory before running |
| `--version` | — | Show version and exit |

### Examples

```bash
# Run interactively (will prompt for dates)
python main.py

# Export records for July 2026
python main.py --start-date 2026-07-01 --end-date 2026-07-31

# Custom output folder, overwrite if it exists
python main.py --export-base ./output --overwrite --start-date 2026-07-01 --end-date 2026-07-31

# Flat export without date subfolder
python main.py --no-timestamp --start-date 2026-07-01 --end-date 2026-07-31

# Export records only for user ID 1234
python main.py --user-id 1234 --start-date 2026-07-01 --end-date 2026-07-31

```

## Windows Executable

No Python installation required. Download the latest `.exe` directly:
**[Download latest release](https://github.com/mi-alkhamis/CMI-Tech-EF45N-DataConverter/releases/latest)**

and run it from the command prompt:

```cmd
CMI-TECH-Data-Converter-v2.0.1.exe
```

Or with options:

```cmd
CMI-TECH-Data-Converter.exe --start-date 2026-07-01 --end-date 2026-07-31
```

> The `.exe` is a self-contained binary — no installer, no dependencies, just download and run.

## Output

The tool scans every `ServiceLog.db` found under `--db-root`, matches each
device directory name to a RAYA device ID, and writes:

| Output | Path | Description |
|---|---|---|
| TXT (RAYA) | `export/<date>/text/<device_id>.txt` | One file per device |
| XLSX | `export/<date>/excel/export.xlsx` | All records in one workbook |

The `<date>` subfolder is today's date and is created automatically
unless `--no-timestamp` is passed.

### TXT (RAYA format)

One file per device containing RAYA attendance sequences, one line per record:

```
3120230215130800030000000301824218
3120230215130900030000000302824218
3120230215131000030000000303824218
```

Format: `[prefix][datetime][entrance_type][user_id][device_id][suffix]`

### XLSX (Excel)

A single workbook with Persian headers:

| شماره کارت | تاریخ | زمان | نوع تردد | کد دستگاه |
|---|---|---|---|---|
| 0000000301 | 2023-02-15 | 13:08 | 0003 | 8242 |
| 0000000302 | 2023-02-15 | 13:09 | 0003 | 8242 |

At the end of each run, a summary is printed to the console:

```
--------------------------------------------------
Summary per device:
Device 8242: 3 user in/out record(s)
```

## Configuration

Device serial-to-RAYA-ID mappings are defined in `DEVICE_ID` inside `main.py`.
Edit the dictionary to match your devices:

```python
DEVICE_ID: dict[str, str] = {
    "150": "8242",
    "151": "9608",
    # add your devices here
}
```

The key is the device folder name (serial), the value is the RAYA device ID.

## Requirements

- Python 3.11 or higher
- [openpyxl](https://pypi.org/project/openpyxl/)

## Error Handling

The tool is designed to be resilient during batch processing:

- Missing or corrupt database files are logged and skipped.
- Unknown device serials produce a warning and are ignored.
- Invalid timestamps are reported per row and skipped.
- A failure on one device does not stop processing of others.

## Contributing

1. Fork this repository.
2. Create a feature branch with a descriptive name.
3. Commit your changes with clear messages.
4. Open a pull request.

## Latest Release

This section is updated automatically from GitHub Releases when a new release is published.

<!-- release-section-start -->
*Release details will appear here after a GitHub release is published.*
<!-- release-section-end -->

## License

Licensed under the [GNU General Public License v3.0](LICENSE).
