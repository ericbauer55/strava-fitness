import pandas as pd
from os.path import join

class Config():
    def __init__(self):
        # Store the absolute path of the project
        # This should be edited if working in a new environment after repo cloning
        self.root_dir = 'C:/Users/Demo/Documents/Data_Science/Strava/strava-fitness/'


    @property
    def raw_ride_path(self):
        return join(self.root_dir, 'data/raw/activities/')

    @property
    def extracted_ride_path(self):
        return join(self.root_dir, 'data/processed/activities/')

    @property
    def enriched_ride_path(self):
        return join(self.root_dir, 'data/enriched/activities/')

    @property
    def activity_log_path(self):
        return join(self.root_dir, 'data/processed/activity_log.csv')

    @property
    def time_gap_threshold(self):
        # This is the number of seconds to create a new segment_id if delta_time >= threshold
        return 15 # seconds