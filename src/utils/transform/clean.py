import pandas as pd
import numpy as np
from haversine import haversine
from scipy import signal

from utils.pandaswindow import PandasWindow

class SignalFilter():
    def __init__(self, df):
        self.df = df

    def run(self):
        self._filter_speed_signal()
        self._filter_grade_signal()

    ################################################################
    # PROCESS METHODS
    ################################################################

    def _filter_speed_signal(self):
        # Apply the is_cruising check over segment windows
        window = PandasWindow(partition_by='segment_id', order_by='time')
        self.df = window.apply_func(df=self.df, func=self.apply_hann_filter_to_speed)

    def _filter_grade_signal(self):
        # Apply the is_cruising check over segment windows
        window = PandasWindow(partition_by='segment_id', order_by='time')
        self.df = window.apply_func(df=self.df, func=self.apply_hann_filter_to_grade)

    ################################################################
    # HELPER METHODS
    ################################################################

    @staticmethod
    def apply_hann_filter_to_speed(df, signal_column='speed', window_order=10):
        signal_list = list(df[signal_column].values)
        win = signal.windows.hann(window_order)
        filtered_signal = signal.convolve(signal_list, win, mode='same') / sum(win)
        
        df['filt_'+signal_column] = np.nan
        if len(signal_list) == len(filtered_signal):
            df['filt_'+signal_column] = filtered_signal
        else:
            df.loc[1:,'filt_'+signal_column] = filtered_signal
            df.loc[0,'filt_'+signal_column] = df.loc[1,'filt_'+signal_column] # backfill
        return df

    @staticmethod
    def apply_hann_filter_to_grade(df, signal_column='grade', window_order=10):
        signal_list = list(df[signal_column].values)
        win = signal.windows.hann(window_order)
        filtered_signal = signal.convolve(signal_list, win, mode='same') / sum(win)
        
        df['filt_'+signal_column] = np.nan
        if len(signal_list) == len(filtered_signal):
            df['filt_'+signal_column] = filtered_signal
        else:
            df.loc[1:,'filt_'+signal_column] = filtered_signal
            df.loc[0,'filt_'+signal_column] = df.loc[1,'filt_'+signal_column] # backfill
        return df



class PrivacyZoner():
    def __init__(self, df, privacy_zone_path):
        self.df = df
        self.privacy_zone_path = privacy_zone_path
        self.df_privacy = None
        self.temporary_prox_columns = []

    def run(self):
        self._read_privacy_zones()
        self._calculate_proximities()
        self._remove_violation_gps_data()
        self._drop_temporary_prox_columns()

    ################################################################
    # PROCESS METHODS
    ################################################################

    def _read_privacy_zones(self):
        self.df_privacy = pd.read_csv(self.privacy_zone_path)

    def _calculate_proximities(self):
        for address_k in range(self.df_privacy.shape[0]):
            # get the relevant parameters
            dist_name = 'prox_' + self.df_privacy.loc[address_k, 'name']
            latitude = self.df_privacy.loc[address_k, 'latitude']
            longitude = self.df_privacy.loc[address_k, 'longitude']
            
            # calculate the proximity
            self.df[dist_name] = self._get_proximity_to_address(latitude, longitude)
            self.temporary_prox_columns.append(dist_name)

    def _remove_violation_gps_data(self):
        for address_k in range(self.df_privacy.shape[0]):
             # get the relevant parameters
            dist_name = 'prox_' + self.df_privacy.loc[address_k, 'name']
            privacy_radius = self.df_privacy.loc[address_k, 'privacy_radius']

            filt_violation = self.df.loc[:,dist_name] <= privacy_radius
            self.df.loc[filt_violation, 'latitude'] = np.nan
            self.df.loc[filt_violation, 'longitude'] = np.nan

    def _drop_temporary_prox_columns(self):
        self.df.drop(self.temporary_prox_columns, axis=1, inplace=True)

    ################################################################
    # HELPER METHODS
    ################################################################

    def _get_proximity_to_address(self, addr_latitude, addr_longitude):
        df_gps = self.df[['latitude', 'longitude']]
        
        # Define an anonymous function to execute over each row to calculate the distance between rows
        haversine_distance = lambda x: haversine((x[0], x[1]), (addr_latitude, addr_longitude), unit='mi')
        
        # Create the distance column, making sure to apply the function row-by-row
        proximity = df_gps.apply(haversine_distance, axis=1)
        
        return proximity
    