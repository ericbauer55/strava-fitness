import pandas as pd
from tqdm import tqdm
from utils.etl import *

if __name__ == '__main__':
    ride_etl_pipeline = RideETL()
    ride_etl_pipeline.run_pipeline()

