import pandas as pd
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
        pass

    def _get_heading(self):
        pass

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

