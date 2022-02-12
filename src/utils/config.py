import pandas as pd

class Config():
    def __init__(self):
        pass

    @staticmethod
    @property
    def raw_ride_path():
        return '../data/raw/activities/'

    @staticmethod
    @property
    def extracted_ride_path():
        return '../data/processed/activities/'

    @staticmethod
    @property
    def enriched_ride_path():
        return '../data/enriched/activities/'

    @staticmethod
    @property
    def activity_log_path():
        return '../data/processed/activity_log.csv'