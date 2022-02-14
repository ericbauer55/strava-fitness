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

class LogETL():
    def __init__(self):
        self.config = Config()
        self.ride_files = None
        self.df_log = None

    def run_pipeline(self):
        # Load Data
        self.load_ride_file_paths()
        self.load_activity_log()
        # Apply Aggregations
        self._get_ride_time_endpoints()
        self._get_row_segment_counts()
        self._get_elapsed_durations()
        self._get_speed_summary()
        self._get_training_window()
        self._get_basic_power_summary()
        self._get_power_ftp()
        # Save Enriched Activity Log
        self.save_activity_log()

    ############################################################################################
    # AGGREGATE
    ############################################################################################

    def _get_ride_time_endpoints(self):
        # Define the Aggregation function to apply
        def get_time_endpoints(df):
            start_time = df.loc[0, 'time']
            end_time = df.loc[df.shape[0]-1, 'time']
            agg_dict = {'start_time':start_time, 'end_time':end_time}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_time_endpoints)

    def _get_row_segment_counts(self):
        # Define the Aggregation function to apply
        def get_row_segment_counts(df):
            row_count = df.shape[0]
            segment_count = len(df['segment_id'].unique())
            agg_dict = {'row_count':row_count, 'segment_count':segment_count}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_row_segment_counts)

    def _get_elapsed_durations(self):
        # Define the Aggregation function to apply
        def get_durations(df):
            last_row = df.shape[0]-1
            elapsed_time = df.loc[last_row, 'elapsed_time']
            moving_time = df.loc[last_row, 'moving_time'] 
            elapsed_distance = df['delta_dist'].cumsum().iloc[last_row]
            elapsed_ascent = df.loc[last_row, 'elapsed_ascent']
            elapsed_descent = df.loc[last_row, 'elapsed_descent']
            elapsed_elevation = df.loc[last_row, 'elapsed_elevation']
            
            agg_dict = {'ride_elapsed_time':elapsed_time, 'ride_moving_time':moving_time, 'elapsed_distance':elapsed_distance, 
                        'elapsed_ascent':elapsed_ascent, 'elapsed_descent':elapsed_descent, 'elapsed_elevation':elapsed_elevation}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_durations)

    def _get_speed_summary(self):
        # Define the Aggregation function to apply
        def get_speed_summary(df):
            ride_avg_speed =  np.mean(df.loc[:, 'speed'])
            
            filt_cruising = df.loc[:,'is_cruising']==True
            ride_cruise_speed = np.mean(df.loc[filt_cruising, 'speed'])
            
            ride_max_speed = np.max(df.loc[:, 'filt_speed'])
            
            agg_dict = {'ride_avg_speed':ride_avg_speed, 'ride_cruise_speed':ride_cruise_speed, 'ride_max_speed':ride_max_speed}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_speed_summary)

    def _get_training_window(self):
        # Define the Aggregation function to apply
        def get_training_window_id(df):
            training_window_id =  df.loc[0, 'training_window_id']
            
            agg_dict = {'training_window_id':training_window_id}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_training_window_id)

    def _get_basic_power_summary(self):
        # Define the Aggregation function to apply
        def get_basic_power_summary(df):
            ride_avg_power = np.mean(df.loc[:, 'inst_power'])    
            ride_max_power = np.max(df.loc[:, 'inst_power'])
            
            agg_dict = {'ride_avg_power':ride_avg_power, 'ride_max_power':ride_max_power}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_basic_power_summary)

    def _get_power_ftp(self):
        # Define the Aggregation function to apply
        def get_power_ftp(df):
            # 1200 corresponds to 1200 samples at 1 sec/sample for 20 minutes
            power_window = df['inst_power'].rolling(window=1200).mean()
            peak_20min_power = np.max(power_window)
            
            agg_dict = {'peak_20min_power':peak_20min_power}
            return agg_dict

        # Apply the Aggregation
        self.apply_aggregation(agg_func=get_power_ftp)

    ############################################################################################
    # HELPERS
    ############################################################################################
    def load_ride_file_paths(self):
        input_rides_path = self.config.cleaned_ride_path
        ride_files = listdir(input_rides_path) # get all files and directories
        ride_files = [join(input_rides_path, f) for f in ride_files if f != '.gitignore'] # add full paths to files
        ride_files = [f for f in ride_files if isfile(f)] # get only files, no directories
        self.ride_files = ride_files

    def load_activity_log(self):
        log_path = self.config.activity_log_path
        self.df_log = pd.read_csv(log_path)
        #self.df_log = self.df_log.set_index('ride_id')

    def save_activity_log(self):
        enriched_log_path = self.config.enriched_activity_log_path
        self.df_log.to_csv(enriched_log_path, index=False)
    
    def apply_aggregation(self, agg_func):
        # Initialize the Aggregation results list
        agg_results = []

        function_name = agg_func.__name__
        print(f'Applying the "{function_name}" aggregation across {len(self.ride_files)} CSV ride files.')
        # Run the Aggregation over each Ride File
        for ride_file in tqdm(self.ride_files):
            # Read the Ride File
            df = read_ride_csv(ride_file)

            # Apply the Aggregation
            agg_dict = agg_func(df)
            ride_id = get_ride_id(ride_file)
            agg_dict['ride_id'] = ride_id

            # Append the results
            agg_results.append(agg_dict)

        # Created aggregation results dataframe
        df_agg = pd.DataFrame(data=agg_results)

        self.df_log = self.df_log.merge(df_agg, on='ride_id', how='inner')

            


class RideETL():
    def __init__(self):
        self.config = Config()

    def run_pipeline(self):
        """
        This is the high-level interface method to run the ETL pipeline in its correct sequence
        """
        #self.extract_gpx_to_csv()
        #self.normalize_time_sampling()
        #self.basic_enrichment()
        #self.protect_privacy_zones()
        #self.filter_noise()
        self.estimate_ride_power()

    ############################################################################################
    # EXTRACT
    ############################################################################################

    def extract_gpx_to_csv(self):
        """
        This method converts all valid raw GPX files found in the Config's Raw_Ride_Path into .CSV files
        """
        # Define the details of the process
        process_details_dict = {'process_func': None,
                                'extract_func': read_gpx_to_dataframe,
                                'input_path': self.config.raw_ride_path,
                                'output_path': self.config.extracted_ride_path,
                                'filter_valid': True,
                                'description_template': 'Extracting {} GPX ride files to CSV'
                                } 

        self.apply_process(process_details_dict=process_details_dict)

    
    ############################################################################################
    # TRANSFORM
    ############################################################################################

    ### NORMALIZATION

    def normalize_time_sampling(self):
        # Define the process function
        threshold = self.config.time_gap_threshold
        def process_normalize_time(df, time_gap_threshold=threshold):
            normalizer = TimeNormalizer(df=df, time_gap_threshold=time_gap_threshold)
            normalizer.run()

            return normalizer.df_upsampled

        # Define the details of the process
        process_details_dict = {'process_func': process_normalize_time,
                                'extract_func': read_ride_csv,
                                'input_path': self.config.extracted_ride_path,
                                'output_path': self.config.enriched_ride_path,
                                'filter_valid': False,
                                'description_template': 'Normalizing the time sampling for {} CSV ride files'
                                } 

        self.apply_process(process_details_dict=process_details_dict)

    ### ENRICHMENT

    def basic_enrichment(self):
        # Define the process function
        def process_basic_enrichment(df):
            enricher = BasicEnricher(df=df)
            enricher.run()

            return enricher.df

        # Define the details of the process
        process_details_dict = {'process_func': process_basic_enrichment,
                                'extract_func': read_ride_csv,
                                'input_path': self.config.enriched_ride_path,
                                'output_path': self.config.enriched_ride_path,
                                'filter_valid': False,
                                'description_template': 'Performing basic enrichments on {} CSV ride files'
                                } 

        self.apply_process(process_details_dict=process_details_dict)

    def estimate_ride_power(self):
        # Define the process function
        calc_params = self.config.power_estimation_params
        log_path = self.config.activity_log_path
        def process_estimate_power(df, calc_params=calc_params, activity_log_path=log_path):
            estimator = PowerEstimator(df=df, calc_params=calc_params, activity_log_path=activity_log_path)
            estimator.run()

            return estimator.df

        # Define the details of the process
        process_details_dict = {'process_func': process_estimate_power,
                                'extract_func': read_ride_csv,
                                'input_path': self.config.cleaned_ride_path,
                                'output_path': self.config.cleaned_ride_path,
                                'filter_valid': False,
                                'description_template': 'Estimating ride power for {} CSV ride files'
                                } 

        self.apply_process(process_details_dict=process_details_dict)

    ### PRIVACY

    def protect_privacy_zones(self):
        # Define the process function
        privacy_zones_file_path = self.config.privacy_zone_path
        def process_protect_privacy(df, privacy_zone_path=privacy_zones_file_path):
            protector = PrivacyZoner(df=df, privacy_zone_path=privacy_zone_path)
            protector.run()

            return protector.df

        # Define the details of the process
        process_details_dict = {'process_func': process_protect_privacy,
                                'extract_func': read_ride_csv,
                                'input_path': self.config.enriched_ride_path,
                                'output_path': self.config.cleaned_ride_path,
                                'filter_valid': False,
                                'description_template': 'Removing sensitive location PII on {} CSV ride files'
                                } 

        self.apply_process(process_details_dict=process_details_dict)


    ### CLEANING

    def filter_noise(self):
        # Define the process function
        def process_filter_noise(df):
            filterer = SignalFilter(df=df)
            filterer.run()

            return filterer.df

        # Define the details of the process
        process_details_dict = {'process_func': process_filter_noise,
                                'extract_func': read_ride_csv,
                                'input_path': self.config.cleaned_ride_path,
                                'output_path': self.config.cleaned_ride_path,
                                'filter_valid': False,
                                'description_template': 'Filtering noisy speed and grade on {} CSV ride files'
                                } 

        self.apply_process(process_details_dict=process_details_dict)

    ############################################################################################
    # HELPERS
    ############################################################################################

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
                df = process(df)

            # Build the new file name for PROCESSED data
            ride_id = get_ride_id(ride_file)
            new_file_name = join(process_details_dict['output_path'], (str(ride_id)+'.csv'))

            # Write the Ride's CSV file
            df.to_csv(new_file_name, index=False)