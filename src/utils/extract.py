import pandas as pd
import gpxpy as gx

def read_gpx_to_dataframe(file_path:str)->pd.DataFrame:
    """
    Given a fully qualified @file_path, this function utilizes the gpxpy
    package to parse the Track Point data from the XML structure.

    This returns a Pandas dataframe of the GPX file
    """
    # Extract the ride ID from the file_path
    ride_id = get_ride_id(file_path=file_path)

    # Setup data capture as lists initially
    data = []

    # Open up the .gpx file and gather each point of data
    with open(file_path,'r') as opened_file:
        # parse the .gpx file into a GPX object
        gpx = gx.parse(opened_file)
        
        # iterate through all tracks, segments and points to extract the data
        for i, track in enumerate(gpx.tracks):
            for j, segment in enumerate(track.segments):
                for point in segment.points:
                    # create the row of data & append to data
                    row = {'ride_id':ride_id, 'segment_id':-1, 'time':point.time, 
                        'elevation':point.elevation, 'latitude':point.latitude, 'longitude':point.longitude}
                    data.append(row)
    
    # Capture the data structure as a Pandas Dataframe
    df = pd.DataFrame(data)

    return df

def get_ride_id(file_path:str)->str:
    """
    This function extracts the ride ID from a file name and returns it as a string
    """
    # Extract the ride ID from the file_path
    ride_id = file_path.split('/')[-1] # grab the file name from the path
    ride_id = ride_id.split('.')[0] # grab the ride ID from file name

    return ride_id

def read_ride_csv(file_path:str, time_columns=['time'])->pd.DataFrame:
    """
    This function loads in a ride's data from .CSV given a file path as a dataframe

    The state of the data (processed vs. enriched) doesn't matter as long
    as there is a 'time' column for the timestamp
    """
    # Read in the CSV file for the Ride
    df = pd.read_csv(file_path)
    
    # guarantee the timestamps are datetime objects
    for time_col in time_columns:
        df[time_col] = pd.to_datetime(df[time_col])

    return df
