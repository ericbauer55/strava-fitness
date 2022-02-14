import pandas as pd
from tqdm import tqdm
from utils.etl import *

if __name__ == '__main__':
    log_aggregation_pipeline = LogETL()
    log_aggregation_pipeline.run_pipeline()

