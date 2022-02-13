from utils.pandaswindow import PandasWindow
from utils.transform.enrich import create_delta_time, create_duration_column


class TimeNormalizer():
    def __init__(self, df, time_gap_threshold):
        self.df = df
        self.df_upsampled = None 
        self.time_gap_threshold = time_gap_threshold

    def run(self):
        self._guarantee_unique_timestamps()
        self.df = create_delta_time(self.df, time_column='time', fill_first=1)
        self.df = create_duration_column(self.df, duration_column_name='elapsed_time')
        self._define_segment_ids()
        self._upsample_time()
        self.df_upsampled = create_duration_column(self.df_upsampled, duration_column_name='moving_time')

    
    ################################################################
    # PROCESS METHODS
    ################################################################

    def _guarantee_unique_timestamps(self):
        # Guarantee that there is only 1 row for each timestamp
        # Not doing this can cause ValueErrors from duplicate time index assignments
        # Timestamps that are equal might also mess with calculations that
        # utilize delta_time 
        self.df = self.df.drop_duplicates(subset=['time'], keep='first')

    def _define_segment_ids(self):
        # get the time gap indices
        time_gap_indices = self._get_time_gap_indices()

        # intialize the initial segment_id. to be incremented for each region of continuous data
        segment_id_counter = 0
        # initialize the starting index of the first segment
        segment_start_index = 0

        for time_gap_index in time_gap_indices:
            # Assign the Segment ID
            self.df.loc[segment_start_index:time_gap_index-1, 'segment_id'] = segment_id_counter
            
            # update the segment_id counter and start index
            segment_id_counter += 1
            segment_start_index = time_gap_index
            
        # Since segment_id == -1 by default, this represents the final segment of activity once parsed
        self.df['segment_id'] = self.df['segment_id'].replace({-1:segment_id_counter})

        # Since the delta_time column is no longer needed to detect discontinuities,
        # Drop delta_time so we can rebuild it at a segment_id level
        self.df.drop(['delta_time'], axis=1, inplace=True)

    def _upsample_time(self):
        # Apply the Resampling/Interpolation at a 1 Hz sample frequency to each segment using a PandasWindow
        window = PandasWindow(partition_by='segment_id', order_by='time')
        self.df_upsampled = window.apply_func(df=self.df, func=self.upsample_and_interpolate)
        
        # Apply the delta_time function across each section
        self.df_upsampled = window.apply_func(df=self.df_upsampled, func=create_delta_time)


    ################################################################
    # HELPER METHODS
    ################################################################

    def _get_time_gap_indices(self):
        # Calculate when the time discontinuities occur
        filt_time_jump = self.df['delta_time'] >= self.time_gap_threshold
        time_gap_indices = list(self.df.loc[filt_time_jump, 'time'].index)
        return time_gap_indices

    @staticmethod
    def upsample_and_interpolate(df, time_column='time', method='linear', limit_direction='forward'):
        # set the timestamp as the index for the dataframe
        df = df.set_index(time_column).copy()
        df_upsampled = df.resample('S').interpolate(method=method, limit_direction=limit_direction).reset_index()
        
        return df_upsampled
