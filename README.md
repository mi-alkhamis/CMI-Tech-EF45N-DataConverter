# CMI-TECH EF45 to RAYA Converter

This project is a Python script that reads DB files from CMI-TECH EF45 devices and converts them to RAYA text in/out sequences to store the employee entrances in the RAYA DB.

## Requirements

- Python 3.6 or higher

## Usage

1. Clone this repository or download the script file.
2. Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```
4. Edit the `DEVICE_ID` dictionary in the script to match your device IDs and RAYA codes.
5. Edit the `DB_PATH` and `EXPORT_PATH` variables in the script to specify the input and output directories.
6. Run the script with `python main.py`.
7. Check the output files in the `EXPORT_PATH` directory.

## Example

Input: A DB file named `ServiceLog.db', containing the following records:

| Timestamp | UserUID | EventType | AdditionalData |
|-----------|---------|-----------|----------------|
| 2023-02-15T13:08:19Z | 0000000301 | Recognition | Allowed |
| 2023-02-15T13:09:23Z | 0000000302 | Recognition | Allowed |
| 2023-02-15T13:10:45Z | 0000000303 | Recognition | Allowed |

Output: A text file in the `export` directory, containing the following lines:

```
3120230215130800030000000301824218
3120230215130900030000000302824218
3120230215131000030000000303824218
```

## Contributing

If you want to contribute to this project, please follow these steps:

1. Fork this repository on GitHub.
2. Create a new branch with a descriptive name.
3. Make your changes and commit them with clear and informative messages.
4. Push your branch to your forked repository.
5. Open a pull request and explain your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details..
