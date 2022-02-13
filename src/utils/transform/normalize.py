from utils.pandaswindow import PandasWindow


class TimeNormalizer():
    def __init__(self, df, time_gap_threshold):
        self.df = df
        self.time_gap_threshold = time_gap_threshold

    def run(self):
        pass


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