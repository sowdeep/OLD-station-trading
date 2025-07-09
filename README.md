# OLD-station-trading
✅
The Python script climate_data_app.py processes climate data from various "stations" for a specific year, as chosen by the user.
Here's a breakdown of its functions:
User Input: It prompts the user to specify the number of climate stations and their names. It also asks the user to input a "target year" for data processing.
Directory Navigation: It sets a base directory, C:\Users\aaa\Desktop\climate data, where it expects to find subfolders for each station. The script validates if these station folders exist.
File Reading and Year Extraction: For the specified target year, it scans each station's folder for .txt files. It extracts a two-digit year from filenames (e.g., .92 for 1992, .05 for 2005) and infers the full four-digit year, assuming years >50 are in the 1900s and _<=50_ are in the 2000s. It reads the second column of these custom space-separated files, converting values to numbers and preserving NaN for non-numeric entries.
Data Consolidation: Data from all relevant files for the target year and each station are combined into a single Pandas DataFrame.
Data Processing:
It adds a 'Day_of_Year' column to the DataFrame.
It calculates the mean of all data columns (excluding 'Day_of_Year') and appends this as a "Mean" row to the DataFrame.
Output: The processed data for the target year, including the 'Mean' row, is saved to an Excel file named processed_climate_data_[year].xlsx in the base directory.
Error Handling: The script includes checks for invalid user input (e.g., non-positive station count, non-integer year), missing base or station directories, and issues during file reading or data extraction.



cd C:\Users\YourUsername\Desktop\ClimateApp
python -m venv venv
.\venv\Scripts\activate
pip install pandas tabulate openpyxl
python climate_data_app.py
