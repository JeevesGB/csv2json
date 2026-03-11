## CSV 2 JSON Converter 

This tool converts .csv files into .json 

made to primarily convert Split Data from Gran Turismo 2 into individual .json files

## How To:

- python gui.py 

- Click "Convert CSVs" and select the folder you wish to convert (subfolders are automatically detected by the tool so for folders with multiple subfolders you only need to select the main)

- You will be then asked where to save the output .json file, it is reccommended to create a new output folder to save the output files to. 

- Once process is completed you can load the .json file into the tool and unlock editing by clicking the "Unlock Edit" button. 

- After you have made your changes you can click "Save" this will then create a -edited.json version of your file keeping the original how it was. 


## This tool uses pandas and PyQt6, you can install these by running this command: 
- pip install -r requirements.txt