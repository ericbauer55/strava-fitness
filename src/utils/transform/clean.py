import pandas as pd
from haversine import haversine

class PrivacyZoner():
    def __init__(self, df, privacy_zone_path):
        self.df = df
        self.privacy_zone_path = privacy_zone_path
        self.df_privacy = None

    def run(self):
        self._read_privacy_zones()
        self._calculate_proximities()
        self._flag_zone_breaches()
        self._remove_breach_gps_data()

    ################################################################
    # PROCESS METHODS
    ################################################################

    def _read_privacy_zones(self):
        self.df_privacy = pd.read_csv(self.privacy_zone_path)

    def _calculate_proximities(self):
        for address_k in self.df_privacy.shape[0]:
            dist_name = 'prox_' + self.df_privacy.loc[address_k, 'name']
            latitude = self.df_privacy.loc[address_k, 'latitude']
            longitude = self.df_privacy.loc[address_k, 'longitude']

            self.df[dist_name] = self._get_proximity_to_address(latitude, longitude)


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
    