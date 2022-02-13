import pandas as pd
import numpy as np
from haversine import haversine
import datetime as dt

from utils.pandaswindow import PandasWindow


def create_delta_time(df, time_column='time', fill_first=1.0):
    df = df.copy()
    # Temporarily get the number of seconds since Jan. 1, 1970 as the UTC timestamp
    df['time_utc'] = df[time_column].apply(lambda x: x.timestamp())
    
    # Calculate the row-wise difference in time (in seconds)
    df['delta_time'] = df['time_utc'].diff()
    
    # drop the temporary time column
    df.drop(['time_utc'], axis=1, inplace=True)
    
    # fill in the initial value of delta_time with @fill_first
    df['delta_time'] = df['delta_time'].fillna(fill_first)
    
    return df

def create_duration_column(df, duration_column_name):
    df[duration_column_name] = df['delta_time'].cumsum()
    return df

class PowerEstimator():
    def __init__(self, df, calc_params):
        self.df = df
        self.calc_params = calc_params
    
    def run(self):
        pass

    ################################################################
    # PROCESS METHODS
    ################################################################

    

    ################################################################
    # HELPER METHODS
    ################################################################





class BasicEnricher():
    def __init__(self, df):
        self.df = df
    
    def run(self):
        self._get_delta_distance()
        self._get_heading()
        self._get_speed()
        self._get_is_cruising()
        self._convert_elevation_units()
        self._get_terrain_grade()
        self._get_elevation_changes()
        self._get_training_window_id()

    ################################################################
    # PROCESS METHODS
    ################################################################

    def _get_delta_distance(self):
        # Apply the distance calculation over segment windows to avoid huge delta_distances
        # at the start of each segment
        window = PandasWindow(partition_by='segment_id', order_by='time')
        self.df = window.apply_func(df=self.df, func=self.compute_distance)

    def _get_heading(self):
        self.df = self.compute_heading(df=self.df)

    def _get_speed(self):
        self.df = self.compute_speed(df=self.df)

    def _get_is_cruising(self):
        # Apply the is_cruising check over segment windows to flag state propogation
        window = PandasWindow(partition_by='segment_id', order_by='time')
        self.df = window.apply_func(df=self.df, func=self.check_is_cruising)

    def _convert_elevation_units(self):
        # We must double check the units of the elevation. 
        # It does not look like the units displayed on Strava's website, but is most likely in meters
        meters_to_feet = 3.281
        self.df['elevation'] = self.df['elevation'] * meters_to_feet

    def _get_terrain_grade(self):
        self.df = self.compute_grade(df=self.df)

    def _get_elevation_changes(self):
        self.df = self.compute_cumulative_elevation_changes(df=self.df)

    def _get_training_window_id(self, training_period=8):
        # Initialize the start date and iteration steps of the training periods
        start = dt.datetime(year=2020, month=1, day=2)
        window_period = dt.timedelta(weeks=training_period)
        
        # Generate a dataframe containing window IDs and their start dates
        data = [{'training_window_id':i, 'start_date':start+window_period*i} for i in range(0,13)]
        df_training_dates = pd.DataFrame(data=data)
        df_training_dates['start_date'] = pd.to_datetime(df_training_dates['start_date']) # make datetime for pandas
        df_training_dates = df_training_dates.set_index('start_date').tz_localize('UTC').sort_index().reset_index() # add TZ for merge

        # Find the window ID via merge_asof
        df_temp = pd.merge_asof(self.df[['time']], df_training_dates, left_on='time', right_on='start_date')

        # Assign the window ID back into the core dataframe
        self.df['training_window_id'] = df_temp['training_window_id']

    ################################################################
    # HELPER METHODS
    ################################################################

    @staticmethod
    def compute_distance(df, latitude='latitude', longitude='longitude', fill_first=np.nan):
        df = df.copy()
        # Copy the previous values of Lat/Long to the current row for vectorized computation
        df['lat_old'] = df[latitude].shift()
        df['long_old'] = df[longitude].shift()
        
        # Grab the relevant columns for distance calculation
        df_gps = df[['lat_old', 'long_old', latitude, longitude]]
        
        # Define an anonymous function to execute over each row to calculate the distance between rows
        haversine_distance = lambda x: haversine((x[0], x[1]), (x[2], x[3]), unit='mi')
        
        # Create the distance column, making sure to apply the function row-by-row
        df['delta_dist'] = df_gps.apply(haversine_distance, axis=1)
        df['delta_dist'] = df['delta_dist'].fillna(fill_first)
        
        # Remove the old latitude and longitude columns
        df.drop(['lat_old','long_old'], axis=1, inplace=True)
        return df

    @staticmethod
    def compute_heading(df, latitude='latitude', longitude='longitude'):
        df = df.copy()
        # Copy the previous values of Lat/Long to the current row for vectorized computation
        df['lat_old'] = df[latitude].shift()
        df['long_old'] = df[longitude].shift()
        
        # Grab the relevant columns for distance calculation
        df_gps = df[['lat_old', 'long_old', latitude, longitude]]
        
        # Define an anonymous function to execute over each row to calculate the angle with North as 0 degrees
        # NOTE: we use "delta_lat / delta_long" to ensure that North = 0 degrees
        rad2deg = 180.0 / np.pi
        haversine_distance = lambda x: rad2deg * np.arctan2((x[2]-x[0]), (x[3]-x[1])) # atan(delta_lat / delta_long)
        
        # Create the distance column, making sure to apply the function row-by-row
        df['heading'] = df_gps.apply(haversine_distance, axis=1)
        df['heading'] = df['heading'].apply(lambda x: x + 360.0*(1-np.sign(x))/2) # correct for negative angles
        
        # Remove the old latitude and longitude columns
        df.drop(['lat_old','long_old'], axis=1, inplace=True)
        return df

    @staticmethod
    def compute_speed(df):
        df = df.copy()
        miles_per_second_2_MPH = 3600.0 / 1.0 # conversion factor
        df['speed'] = miles_per_second_2_MPH * df['delta_dist'] / df['delta_time']
        return df

    @staticmethod
    def check_is_cruising(df, upper_threshold=8, lower_threshold=5):
        df = df.copy().reset_index()
        
        df['is_cruising'] = False
        
        for k in range(1, df.shape[0]):
            previous_state = df.loc[k-1,'is_cruising']
            current_speed = df.loc[k,'speed']
            if (previous_state==False) & (current_speed >= upper_threshold):
                df.loc[k,'is_cruising'] = True # rising threshold surpassed
            elif (previous_state==True) & (current_speed < lower_threshold):
                df.loc[k,'is_cruising'] = False # falling threshold exceeded
            else:
                # if there is no change, propogate the previous state
                df.loc[k,'is_cruising'] = df.loc[k-1,'is_cruising']
        
        return df

    @staticmethod
    def compute_grade(df, fill_first=0.0):
        df = df.copy()
        
        # create an elevation difference
        feet_to_miles = 1.0 / 5280.0
        df['delta_ele'] = df['elevation'].diff() * feet_to_miles
        df['delta_ele'] = df['delta_ele'].fillna(fill_first)
        
        # create the grade column as a percent
        df['grade'] = 100.0 * (df['delta_ele'] / df['delta_dist'])
        
        # drop the elevation difference
        df.drop(['delta_ele'], axis=1, inplace=True)
        
        return df

    @staticmethod
    def compute_cumulative_elevation_changes(df, fill_first=0.0):
        df = df.copy()
        
        # create an elevation difference
        df['delta_ele'] = df['elevation'].diff()
        df['delta_ele'] = df['delta_ele'].fillna(fill_first)
        
        # create delta ascent and delta descent columns
        df['delta_ascent'] = df.loc[df['delta_ele']>=0, 'delta_ele']
        df['delta_descent'] = df.loc[df['delta_ele']<=0, 'delta_ele']
        
        # create the cumulative versions
        df['elapsed_ascent'] = df['delta_ascent'].cumsum()
        df['elapsed_ascent'] = df['elapsed_ascent'].interpolate() # fill in any blanks
        df['elapsed_descent'] = df['delta_descent'].cumsum()
        df['elapsed_descent'] = np.abs(df['elapsed_descent'].interpolate()) # fill in any blanks
        
        # create the total elevation change column
        df['elapsed_elevation'] = df['elapsed_ascent'] + df['elapsed_descent']
            
        # drop the elevation differences
        df.drop(['delta_ele','delta_ascent','delta_descent'], axis=1, inplace=True)
        
        return df