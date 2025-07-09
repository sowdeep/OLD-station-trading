import os
import re
import pandas as pd
import calendar
from tabulate import tabulate # For displaying tables in the console

def extract_year_from_filename(filename):
    """
    Extracts the four-digit year from a filename like 'AS010319.92' or 'AS010319.92.txt'.
    Adjusts century inference (1900s vs 2000s) based on the two-digit year.
    """
    # Look for .XX pattern anywhere before an optional file extension
    match = re.search(r'\.(\d{2})(?:\.[^.]*)?$', filename, re.IGNORECASE)

    if match:
        two_digit_year = int(match.group(1))

        # Heuristic for century determination:
        # If the two-digit year is above 50 (e.g., 99, 86), assume 1900s.
        # If it's 50 or below (e.g., 00, 05, 24), assume 2000s.
        if two_digit_year > 50:
            full_year = 1900 + two_digit_year
        else:
            full_year = 2000 + two_digit_year
        
        return full_year
    return None # Return None if year pattern is not found

def read_custom_space_separated_file(filepath):
    """
    Attempts to read data from a custom space-separated text file,
    skipping the first column and extracting the second.
    This version PRESERVES all values from the 2nd column, including non-numeric ones.
    """
    try:
        # Use delim_whitespace=True for robust space-separated parsing.
        # header=None: assumes no header row.
        df = pd.read_csv(filepath, header=None, delim_whitespace=True)
        
        # Ensure there's a second column (index 1) to extract
        if df.shape[1] < 2:
            raise ValueError("File does not contain at least two columns after space-separation.")
            
        # Select the 2nd column (index 1).
        # We convert to numeric with errors='coerce' but DO NOT dropna() here.
        # This will turn truly non-numeric values into NaN, but keep the row.
        extracted_data = pd.to_numeric(df.iloc[:, 1], errors='coerce')
        
        print(f"    Successfully read as custom space-separated: {os.path.basename(filepath)}")
        return extracted_data # Return the series with NaNs if present

    except Exception as e:
        print(f"    Could not read {os.path.basename(filepath)} as custom space-separated: {e}. Skipping file.")
        return None

def run_climate_processor():
    # 1. User Input and Configuration
    while True:
        try:
            num_stations = int(input("How many stations? "))
            if num_stations <= 0:
                print("Please enter a positive number of stations.")
                continue
            break
        except ValueError:
            print("Invalid input! Please enter a valid integer for the number of stations.")

    station_names = [] # Initialize an empty list for station names
    print("\n--- Please name your stations ---")
    for i in range(num_stations):
        while True:
            name = input(f"Enter name for Station {i + 1}: ").strip()
            if name: # Ensure name is not empty
                station_names.append(name)
                break
            else:
                print("Station name cannot be empty. Please enter a valid name.")

    # Prepare data for tabulation
    table_data = [[i + 1, name] for i, name in enumerate(station_names)]
    headers = ["#", "Station Name"] # Initialize headers list

    print("\n--- Confirmed Stations ---")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("--------------------------\n")

    while True:
        try:
            target_year = int(input("Which year data? "))
            if not (1900 <= target_year <= 2099): # Broad range covering likely climate data
                print(f"Please enter a realistic year (e.g., between 1900 and 2099).")
                continue
            break
        except ValueError:
            print("Invalid input! Please enter a valid integer for the year.")

    # 2. Navigating Climate Data Directories
    base_path = r"C:\Users\aaa\Desktop\climate data"

    # Verify base path existence
    if not os.path.isdir(base_path):
        print(f"Error: Base directory '{base_path}' not found. Please ensure the path is correct.")
        print("Exiting application.")
        return

    valid_station_paths = []
    print("\n--- Validating Station Folders ---")
    for station_name in station_names:
        station_folder_path = os.path.join(base_path, station_name)
        if os.path.isdir(station_folder_path):
            valid_station_paths.append(station_folder_path)
            print(f"Found folder for '{station_name}': {station_folder_path}")
        else:
            print(f"Warning: Folder for '{station_name}' not found at '{station_folder_path}'. Skipping.")

    if not valid_station_paths:
        print("No valid station folders found. Exiting application.")
        return

    all_station_series = {} # Dictionary to hold Series for each station

    print(f"\n--- Processing data for year {target_year} ---")
    for station_path in valid_station_paths:
        station_name = os.path.basename(station_path)
        current_station_data_parts = [] # To hold data from multiple files for this station for the target year
        found_files_for_station_year = False # Flag to track if any relevant files were found

        for file_name in os.listdir(station_path):
            file_path = os.path.join(station_path, file_name)

            # Skip directories, process only files
            if os.path.isdir(file_path):
                print(f"  - Skipping {file_name}: It's a directory.")
                continue

            file_year = extract_year_from_filename(file_name)

            if file_year == target_year:
                found_files_for_station_year = True # At least one relevant file found
                print(f"  - Found file for target year ({file_year}): {file_name}. Attempting to read...")
                extracted_data = read_custom_space_separated_file(file_path) # Call the specialized reader

                if extracted_data is not None: # Check if reading was successful (even if it contains NaNs)
                    current_station_data_parts.append(extracted_data)
                else:
                    print(f"    Failed to extract data from {file_name}. Skipping this file.")
            else:
                if file_year is None:
                    print(f"  - Skipping file {file_name}: Year pattern (.XX) not found in filename.")
                else:
                    print(f"  - Skipping file {file_name}: Detected year {file_year} does not match target year {target_year}.")

        if current_station_data_parts:
            # Concatenate all data parts found for this station for the target year
            combined_station_series = pd.concat(current_station_data_parts, ignore_index=True)
            all_station_series[f"{station_name}_Data"] = combined_station_series
        elif not found_files_for_station_year:
            print(f"  No files matching target year {target_year} were found for station '{station_name}'.")
        else: # Relevant files were found, but none yielded usable data
            print(f"  No valid data could be extracted from any files for station '{station_name}' for year {target_year}.")

    if not all_station_series:
        print("No data collected from any station for the specified year. Exiting application.")
        return

    # Consolidate all station data into a single DataFrame
    # Aligning by index is crucial here. Shorter series will be padded with NaN.
    # This automatically fills missing rows with NaN, preserving structure.
    df_consolidated = pd.concat(all_station_series.values(), axis=1)
    df_consolidated.columns = all_station_series.keys() # Assign meaningful column names for the table

    # 4. Processing Data (Add Day_of_Year Column)
    is_leap = calendar.isleap(target_year)
    days_in_year = 366 if is_leap else 365
    print(f"The year {target_year} {'is' if is_leap else 'is not'} a leap year, with {days_in_year} days.")

    # Generate the 'Day_of_Year' column.
    # The length of this column should match the longest data series present.
    # Using df_consolidated.shape[0] directly for max_data_length.
    max_data_length = df_consolidated.shape[0] # Get current number of rows in consolidated data
    days_column = list(range(1, max_data_length + 1))

    df_processed = df_consolidated.copy()
    day_series = pd.Series(days_column, index=df_processed.index) # Create with matching index
    df_processed.insert(0, 'Day_of_Year', day_series)

    # 5. Calculating and Appending Column Means
    # Exclude 'Day_of_Year' from mean calculation
    data_columns = df_processed.columns[1:] # All columns except the first ('Day_of_Year')
    
    # Calculate mean ONLY on numeric parts of the data columns.
    # Pandas .mean() method automatically ignores NaN values, which is exactly what we need.
    column_means = df_processed[data_columns].mean(axis=0)

    # Prepare the mean row for appending
    mean_row_series = pd.Series(dtype=object) # Use object dtype to allow for "Mean" string
    mean_row_series['Day_of_Year'] = "Mean" # Placeholder string for the first column
    for col, mean_val in column_means.items():
        mean_row_series[col] = mean_val
    
    # Append the mean row to the DataFrame
    df_final = pd.concat([df_processed, pd.DataFrame([mean_row_series])], ignore_index=True)

    # 6. Exporting Processed Data to Excel
    output_filename = f"processed_climate_data_{target_year}.xlsx"
    output_path = os.path.join(base_path, output_filename) # Save in the base climate data folder
    
    try:
        df_final.to_excel(output_path, index=False) # Do not write DataFrame index to Excel
        print(f"\nProcessed data successfully saved to: {output_path}")
    except Exception as e:
        print(f"\nError saving processed data to {output_path}: {e}")

if __name__ == "__main__":
    run_climate_processor()