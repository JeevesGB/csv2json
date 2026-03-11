import pandas as pd
import os
import json

def merge_csv_to_json(csv_directory, output_json):
    """
    Merges all CSV files in a directory (including subdirectories) into a single JSON file.
    Adds the file or subfolder name to each record.
    """
    data_list = []

    for root, dirs, files in os.walk(csv_directory):
        for filename in files:
            if filename.endswith('.csv'):
                file_path = os.path.join(root, filename) 
                
                df = pd.read_csv(file_path)
                
                for _, record in df.iterrows():
                    record_dict = record.to_dict() 
                    record_dict['source_file'] = filename 
                    record_dict['source_folder'] = os.path.basename(root)  
                
                    data_list.append(record_dict)

    with open(output_json, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)

    print(f"Merged data saved to {output_json}")