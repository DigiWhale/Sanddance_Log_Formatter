import os
import pandas as pd
import sys
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from turfpy import measurement
from geojson import Point, Feature

def import_csv_as_df(csv_file):
  """
  Function to import a csv file as a pandas dataframe.
  """
  df = pd.read_csv(csv_file)
  return df

def get_bearing(lat1, lat2, lon1, lon2):
  brng = Geodesic.WGS84.Inverse(lat1, lon1, lat2, lon2)['azi2']
  return brng
  
def get_turf_bearing(lat1, lat2, lon1, lon2):
  start = Feature(geometry=Point((lon1, lat1)))
  end = Feature(geometry=Point((lon2, lat2)))
  brng = measurement.bearing(start,end)
  return brng

def calculate_drift(open_path, save_path):
  """
  Function to iterate through all files in a folder and return a list of
  dataframes.
  """
  for root, subdirectories, files in os.walk(open_path):
    for folder in subdirectories:
      print(folder)
      try:
        coordinates = pd.read_csv(root + '/' + folder + '/' + 'rpi-coordinates.csv')
        drift = []
        gps_heading = []
        rpi_heading = []
        prev_rpi_lat = coordinates['rpi_lat'].iloc[0]
        prev_rpi_lon = coordinates['rpi_lon'].iloc[0]
        prev_gps_lat = coordinates['gps_lat'].iloc[0]
        prev_gps_lon = coordinates['gps_lon'].iloc[0]
        for index, row in coordinates.iterrows():
          # print(row['rpi_lat'], row['rpi_lon'], row['gps_lat'], row['gps_lon'])
          coords_1 = (row['rpi_lat'], row['rpi_lon'])
          coords_2 = (row['gps_lat'], row['gps_lon'])
          # print(geodesic(coords_1, coords_2).km * 1000, 'meters')
          drift.append(geodesic(coords_1, coords_2).km * 1000)
          gps_bearing = get_turf_bearing(prev_gps_lat, row['gps_lat'], prev_gps_lon, row['gps_lon'])
          rpi_bearing = get_turf_bearing(prev_rpi_lat, row['rpi_lat'], prev_rpi_lon, row['rpi_lon'])
          if rpi_bearing < 0:
            rpi_bearing = rpi_bearing + 360
          rpi_heading.append(rpi_bearing)
          if gps_bearing < 0:
            gps_bearing = gps_bearing + 360
          gps_heading.append(gps_bearing)
          prev_gps_lon = row['gps_lon']
          prev_gps_lat = row['gps_lat']
          prev_rpi_lon = row['rpi_lon']
          prev_rpi_lat = row['rpi_lat']
        coordinates['drift_between_rpi_and_gps'] = drift
        coordinates['gps_bearing'] = gps_heading
        coordinates['rpi_bearing'] = rpi_heading
        coordinates.to_csv(root + '/' + folder + '/' + 'rpi-coordinates-analyzed.csv', index=False)
      except:
        print(sys.exc_info(), root + '/' + folder + '/')

if __name__ == '__main__':
  open_path = "/home/pi/MSRS-RPI/logs"
  save_path = "/home/pi/MSRS-RPI/logs"
  calculate_drift(open_path, save_path)