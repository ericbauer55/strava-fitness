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
    def cleaned_ride_path(self):
        return join(self.root_dir, 'data/cleaned/activities/')

    @property
    def activity_log_path(self):
        return join(self.root_dir, 'data/processed/activity_log.csv')

    @property
    def enriched_activity_log_path(self):
        return join(self.root_dir, 'data/cleaned/activity_log.csv')

    @property
    def privacy_zone_path(self):
        # NOTE: this directory is in .gitignore
        return join(self.root_dir, 'data/cleaned/privacy/privacy_zones.csv')

    @property
    def time_gap_threshold(self):
        # This is the number of seconds to create a new segment_id if delta_time >= threshold
        return 15 # seconds

    @property
    def power_estimation_params(self):
        params = {'rider_mass': 86.1826, # kg
                  'area': 0.4635862, # m^2
                  'mu_rr': 0.005, # coefficient of rolling friction
                  'c_drag': 0.95, # coefficient of drag
                  'rho_air': 1.2, # kg/m^3 air density
                  'eta_dt': 0.96, # efficiency of drive train
                  'gravity': 9.8 # m/s^2
                 }
        return params # seconds