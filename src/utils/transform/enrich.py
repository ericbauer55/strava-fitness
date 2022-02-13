import pandas as pd
import numpy as np
from haversine import haversine

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
        pass

    def _get_is_cruising(self):
        pass

    def _convert_elevation_units(self):
        pass

    def _get_terrain_grade(self):
        pass

    def _get_elevation_changes(self):
        pass

    def _get_training_window_id(self):
        pass

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