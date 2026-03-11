import pandas as pd
import os
import json

def merge_csv_to_json(csv_directory, output_json):
    """
    Merges all CSV files in a directory (including subdirectories) into a single JSON file.
    """
    data_list = []

    # Walk through all directories and subdirectories
    for root, dirs, files in os.walk(csv_directory):
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(root, filename)  # Get the full path of the CSV file
                
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(file_path)
                
                # Convert the DataFrame to a list of dictionaries and append it to data_list
                data_list.extend(df.to_dict(orient='records'))

    # Write the combined data to a JSON file
    with open(output_json, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)

    print(f"Merged data saved to {output_json}")