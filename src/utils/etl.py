import pandas as pd
from tqdm import tqdm
from os import listdir
from os.path import isfile, join

from utils.config import Config
from utils.extract import *
from utils.transform.clean import *
from utils.transform.enrich import *
from utils.transform.convert import *
from utils.transform.normalize import *

class RideETL():
    def __init__(self):
        self.config = Config()

    def run_pipeline(self):
        """
        This is the high-level interface method to run the ETL pipeline in its correct sequence
        """
        self.extract_gpx_to_csv()
        self.normalize_time_sampling()

    ############################################################################################
    # EXTRACT
    ############################################################################################

    def extract_gpx_to_csv(self):
        """
        This method converts all valid raw GPX files found in the Config's Raw_Ride_Path into .CSV files
        """
        # Get the list of raw activity files
        raw_rides_path = self.config.raw_ride_path
        raw_ride_files = listdir(raw_rides_path) # get all files and directories
        raw_ride_files = [join(raw_rides_path, f) for f in raw_ride_files if f != '.gitignore'] # add full paths to files
        raw_ride_files = [f for f in raw_ride_files if isfile(f)] # get only files, no directories

        # Filter the activity files for only the valid ones
        valid_raw_ride_files = self._select_valid_rides(raw_ride_files)

        print(f'Extracting {len(valid_raw_ride_files)} GPX ride files to CSV')
        for ride_file in tqdm(valid_raw_ride_files):
            # Read the Ride's GPX file
            df = read_gpx_to_dataframe(ride_file)

            # Build the new file name for PROCESSED data
            ride_id = get_ride_id(ride_file)
            new_file_name = join(self.config.extracted_ride_path, (str(ride_id)+'.csv'))

            # Write the Ride's CSV file
            df.to_csv(new_file_name, index=False)

    def _select_valid_rides(self, file_names):
        """
        Given a list of @file_names of potential ride files, this method refers to the processed Activity Log.
        For all files with ride_id's in the Log, these ride files are retained as valid rides and returned.
        """
        # Read the list of non-manually uploaded, Ride-type activities
        df_log_valid = pd.read_csv(self.config.activity_log_path)
        df_log_valid = df_log_valid['ride_id'].to_frame() # select only the ride_id column

        # Build the @file_names into a dataframe of "ride_id" | "file_name" columns
        data = [{'ride_id':int(get_ride_id(ride_file)), 'file_name':ride_file} for ride_file in file_names]
        df_files = pd.DataFrame(data=data)

        # Subset the ride_ids that appear in df_log_valid
        df_valid = df_log_valid.merge(df_files, on='ride_id', how='inner')

        # Return the list of file names that correspond to valid ride_ids
        valid_file_names = list(df_valid['file_name'].values)
        return valid_file_names

    ############################################################################################
    # TRANSFORM
    ############################################################################################

    ### NORMALIZATION

    def normalize_time_sampling(self):
        # Get the list of extracted activity files as .csv's
        extracted_rides_path = self.config.extracted_ride_path
        extracted_ride_files = listdir(extracted_rides_path) # get all files and directories
        extracted_ride_files = [join(extracted_rides_path, f) for f in extracted_ride_files if f != '.gitignore'] # add full paths to files
        extracted_ride_files = [f for f in extracted_ride_files if isfile(f)] # get only files, no directories

        # There is no need to filter for valid ride_id's since this is taken care of by `extract_gpx_to_csv`

        print('-'*100)
        print(f'Normalizing the time sampling for {len(extracted_ride_files)} CSV ride files')
        for ride_file in tqdm(extracted_ride_files):
            # Read the Ride's CSV file
            df = read_ride_csv(ride_file)

            # Run the data through the normalization process
            normalizer = TimeNormalizer(df=df, time_gap_threshold=self.config.time_gap_threshold)
            normalizer.run()

            df = normalizer.df_upsampled

            # Build the new file name for ENRICHED data
            ride_id = get_ride_id(ride_file)
            new_file_name = join(self.config.enriched_ride_path, (str(ride_id)+'.csv'))

            # Write the Ride's CSV file
            df.to_csv(new_file_name, index=False)

    ############################################################################################
    # HELPERS
    ############################################################################################

    def apply_process(self, process_details_dict):
        """
        process_details_dict = {'process_func': function object for specific process to run,
                                'extract_func': function object for the extraction step
                                'input_path': input path to extract from
                                'output_path': output path to load to
                                'filter_valid': True/False of whether to use _select_valid_rides
                                'description_template': string template to fill out and print when running
                                }
        """
        # Get the list of activity files
        input_rides_path = process_details_dict['input_path']
        ride_files = listdir(input_rides_path) # get all files and directories
        ride_files = [join(input_rides_path, f) for f in ride_files if f != '.gitignore'] # add full paths to files
        ride_files = [f for f in ride_files if isfile(f)] # get only files, no directories

        # Filter the activity files for only the valid ones
        if process_details_dict['filter_valid'] == True:
            ride_files = self._select_valid_rides(ride_files)

        # Print Process Description
        print('-'*100)
        process_description = process_details_dict['description_template'].format(len(ride_files))
        print(process_description)

        # Run the Process over each Ride File
        for ride_file in tqdm(ride_files):
            # Read the Ride File
            df = process_details_dict['extract_func'](ride_file)

            # Apply the Process (if any specified)
            process = process_details_dict['process_func']
            if process is not None:
                df = process(ride_file)

            # Build the new file name for PROCESSED data
            ride_id = get_ride_id(ride_file)
            new_file_name = join(process_details_dict['output_path'], (str(ride_id)+'.csv'))

            # Write the Ride's CSV file
            df.to_csv(new_file_name, index=False)