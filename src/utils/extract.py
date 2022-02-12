import pandas as pd
import gpxpy as gx

def read_gpx_to_dataframe(file_path):
    # Extract the ride ID from the file_path
    ride_id = get_ride_id(file_path=file_path)

    # Setup data capture as lists initially
    data = []

    # Open up the .gpx file and gather each point of data
    with open(file_path,'r') as opened_file:
        # parse the .gpx file into a GPX object
        try:
            gpx = gx.parse(opened_file)
        
            # iterate through all tracks, segments and points to extract the data
            for i, track in enumerate(gpx.tracks):
                for j, segment in enumerate(track.segments):
                    for point in segment.points:
                        # create the row of data & append to data
                        row = {'track':ride_id, 'segment_id':j, 'time':point.time, 
                            'elevation':point.elevation, 'latitude':point.latitude, 'longitude':point.longitude}
                        data.append(row)
        except UnicodeDecodeError:
            print(f'UnicodeDecodeError detected on file="{file_path}"')
    
    # Capture the data structure as a Pandas Dataframe
    df = pd.DataFrame(data)

    return df

def get_ride_id(file_path):
    # Extract the ride ID from the file_path
    ride_id = file_path.split('/')[-1] # grab the file name from the path
    ride_id = ride_id.split('.gpx')[0] # grab the ride ID from file name

    return ride_id

def read_ride_csv(file_path):
    # Read in the CSV file for the Ride
    df = pd.read_csv(file_path)
    
    # guarantee the timestamps are datetime objects
    df['time'] = pd.to_datetime(df['time'])

    return df
