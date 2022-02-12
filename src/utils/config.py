import pandas as pd

class Config():
    def __init__(self):
        pass

    @property
    def raw_ride_path(self):
        return '../data/raw/activities/'

    @property
    def extracted_ride_path(self):
        return '../data/processed/activities/'

    @property
    def enriched_ride_path(self):
        return '../data/enriched/activities/'

    @property
    def activity_log_path(self):
        return '../data/processed/activity_log.csv'