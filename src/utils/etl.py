import pandas as pd
from utils.extract import *
from utils.config import Config
from tqdm import tqdm
from os import listdir
from os.path import isfile, join


class RideETL():
    def __init__(self):
        self.config = Config()

    def extract_gpx_to_csv(self):
        # Get the list of raw activity files
        raw_ride_files = listdir(self.config.raw_ride_path) # get all files and directories
        raw_ride_files = [f for f in raw_ride_files if isfile(join(self.config.raw_ride_path, f))] # get only files

        # Filter the activity files for only the valid ones
        raw_ride_files = self._select_valid_rides(raw_ride_files)

        print(f'Extracting {len(raw_ride_files)} GPX ride files to CSV')
        for ride_file in tqdm(raw_ride_files):
            # Read the Ride's GPX file
            df = read_gpx_to_dataframe(ride_file)
            # Build the new file name
            ride_id = get_ride_id(ride_file)
            new_file_name = join(self.config.extracted_ride_path, (str(ride_id)+'.csv'))
            # Write the Ride's CSV file
            df.to_csv(new_file_name, index=False)


    def _select_valid_rides(self, file_names):
        df_log = pd.read_csv(self.config.activity_log_path)