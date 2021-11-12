import os
import pandas as pd
import sys
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic
from turfpy import measurement
from geojson import Point, Feature
import math
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
px.set_mapbox_access_token(os.environ.get("MAPBOX"))

def import_csv_as_df(csv_file):
  """
  Function to import a csv file as a pandas dataframe.
  """
  df = pd.read_csv(csv_file)
  return df

def calculate_new_coordinates(prev_lat, prev_lon, heading, distance):
  R = 6378.1 #Radius of the Earth
  brng = heading * (math.pi / 180) #Heading is converted to radians.
  d = distance/1000 #meters to distance in km
  lat1 = prev_lat * (math.pi / 180) #Current lat point converted to radians
  lon1 = prev_lon * (math.pi / 180) #Current lon point converted to radians
  lat2 = math.asin(math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng)) # calculate new lat point
  lon2 = lon1 + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2)) # calculate new lon point
  lat2 = math.degrees(lat2) # convert to degrees
  lon2 = math.degrees(lon2) # convert to degrees
  return {'lat': lat2, 'lon': lon2} # return new coordinates
      

def plot_coordinates_on_mapbox(df, save_path):
  """
  Function to plot coordinates on a mapbox map.
  """
  try:
    fig = px.scatter_mapbox(df, lat='rpi_lat', lon='rpi_lon', zoom=18, color='gps_minus_rpi_bearing', center={'lat': df['rpi_lat'][0], 'lon': df['rpi_lon'][0]}, hover_data=["drift_between_rpi_and_gps_meters", "average_drift", "doppler_compensation_factor", "experimental_heading", "rpi_bearing"])
    fig2 = px.scatter_mapbox(df, lat='msrs_lat', lon='msrs_lon', zoom=18, color_discrete_sequence=['blue'], hover_data=["drift_between_rpi_and_gps_meters", "average_drift", "doppler_compensation_factor", "experimental_heading", "rpi_bearing"])
    fig3 = px.scatter_mapbox(df, lat='gps_lat', lon='gps_lon', zoom=18, color_discrete_sequence=['#39ff14'], color_continuous_scale='Bluered_r', hover_data=["drift_between_rpi_and_gps_meters", "average_drift", "doppler_compensation_factor", "experimental_heading", "rpi_bearing"])
    fig4 = px.scatter_mapbox(df, lat='experimental_lat', lon='experimental_lon', zoom=18, color_discrete_sequence=['#39ffff'], color_continuous_scale='Bluered_r', hover_data=["drift_between_rpi_and_gps_meters", "average_drift", "doppler_compensation_factor", "experimental_heading", "rpi_bearing"])
    fig.add_trace(fig2.data[0])
    fig.add_trace(fig3.data[0])
    fig.add_trace(fig4.data[0])
    fig.update_layout(mapbox_style="dark")
    fig.write_html(save_path)
  except Exception as e:
    print(sys.exc_info()[0], save_path, e)

def get_turf_distance(lat1, lat2, lon1, lon2):
  start = Feature(geometry=Point((lon1, lat1)))
  end = Feature(geometry=Point((lon2, lat2)))
  dist = measurement.distance(start,end)
  return dist

def calculate_compass_bearing(lat1, lat2, lon1, lon2):
  pointA = (lat1, lon1)
  pointB = (lat2, lon2)
  if (type(pointA) != tuple) or (type(pointB) != tuple):
      raise TypeError("Only tuples are supported as arguments")
  lat1 = math.radians(pointA[0])
  lat2 = math.radians(pointB[0])
  diffLong = math.radians(pointB[1] - pointA[1])
  x = math.sin(diffLong) * math.cos(lat2)
  y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
  initial_bearing = math.atan2(x, y)
  initial_bearing = math.degrees(initial_bearing)
  compass_bearing = (initial_bearing + 360) % 360
  return compass_bearing

def calculate_drift(open_path, save_path):
  """
  Function to iterate through all files in a folder and return a list of
  dataframes.
  """
  for root, subdirectories, files in os.walk(open_path):
    for folder in subdirectories:
      print(folder)
      if folder == "11-10-2021-19-05-42":
        try:
          coordinates = pd.read_csv(root + '/' + folder + '/' + 'rpi-coordinates.csv')
          
          start_row_range = 0
          end_row_range = 100
          max_end_row_range = len(coordinates)
          
          compass_vehicle_alignment_error = -2.5
          doppler_compensation_factor = 1.017
          
          drift = []
          gps_minus_rpi_bearing_difference = []
          gps_heading = []
          rpi_heading = []
          gps_distance_from_prev_coord = []
          rpi_distance_from_prev_coord = []
          gps_distance_minus_rpi_distance = []
          experimental_lat = []
          experimental_lon = []
          average_drift_array = []
          average_distance_array = []
          doppler_compensation_factor_array = []
          experimental_heading_array = []
          
          prev_rpi_lat = coordinates['rpi_lat'].iloc[0]
          prev_rpi_lon = coordinates['rpi_lon'].iloc[0]
          prev_gps_lat = coordinates['gps_lat'].iloc[0]
          prev_gps_lon = coordinates['gps_lon'].iloc[0]
          prev_rpi_bearing = 0
          prev_gps_bearing = 0
          
          for index, row in coordinates.iterrows():
            gps_bearing = calculate_compass_bearing(prev_gps_lat, row['gps_lat'], prev_gps_lon, row['gps_lon'])
            rpi_bearing = calculate_compass_bearing(prev_rpi_lat, row['rpi_lat'], prev_rpi_lon, row['rpi_lon'])
            gps_dist = get_turf_distance(prev_gps_lat, row['gps_lat'], prev_gps_lon, row['gps_lon'])
            rpi_dist = get_turf_distance(prev_rpi_lat, row['rpi_lat'], prev_rpi_lon, row['rpi_lon'])
            drift_distance = geodesic((row['rpi_lat'], row['rpi_lon']), (row['gps_lat'], row['gps_lon'])).km * 1000
            if rpi_bearing < 0:
              rpi_bearing = rpi_bearing + 360
            if gps_bearing < 0:
              gps_bearing = gps_bearing + 360
            if rpi_bearing == 0:
              rpi_bearing = prev_rpi_bearing
            if gps_bearing == 0:
              gps_bearing = prev_gps_bearing
              
            drift.append(drift_distance)
            rpi_heading.append(rpi_bearing)
            gps_heading.append(gps_bearing)
            gps_minus_rpi_bearing_difference.append(gps_bearing - rpi_bearing)
            gps_distance_from_prev_coord.append(gps_dist*1000)
            rpi_distance_from_prev_coord.append(rpi_dist*1000)
            gps_distance_minus_rpi_distance.append(gps_dist*1000 - rpi_dist*1000)
            
            prev_rpi_bearing = rpi_bearing
            prev_gps_bearing = gps_bearing
            prev_gps_lon = row['gps_lon']
            prev_gps_lat = row['gps_lat']
            prev_rpi_lon = row['rpi_lon']
            prev_rpi_lat = row['rpi_lat']
            
          coordinates['gps_minus_rpi_bearing'] = gps_minus_rpi_bearing_difference
          coordinates['drift_between_rpi_and_gps_meters'] = drift
          coordinates['gps_bearing'] = gps_heading
          coordinates['rpi_bearing'] = rpi_heading
          coordinates['gps_distance_from_prev_coord_meters'] = gps_distance_from_prev_coord
          coordinates['rpi_distance_from_prev_coord_meters'] = rpi_distance_from_prev_coord
          coordinates['gps_distance_minus_rpi_distance_meters'] = gps_distance_minus_rpi_distance
          
          average_distance_between_rpi_and_gps = coordinates["gps_distance_minus_rpi_distance_meters"].mean()
          
          new_lat = coordinates['gps_lat'].iloc[0]
          new_lon = coordinates['gps_lon'].iloc[0]
          
          average_drift = coordinates["gps_minus_rpi_bearing"].iloc[start_row_range:end_row_range].mean()
          print('average drift', average_drift)
          
          for index, row in coordinates.iterrows():
            
            if index % 100 == 0:
              if max_end_row_range > start_row_range + 100:
                start_row_range += 100
              if max_end_row_range > end_row_range + 100:
                end_row_range += 100
              else:
                end_row_range = max_end_row_range
              average_drift = coordinates["gps_minus_rpi_bearing"].iloc[start_row_range:end_row_range].mean()
              print('average drift', average_drift)
            if abs(average_drift) < 10:  
              new_position = calculate_new_coordinates(new_lat, new_lon, average_drift + row['rpi_bearing'] + compass_vehicle_alignment_error, row['rpi_distance_from_prev_coord_meters'] * doppler_compensation_factor)
              experimental_heading_array.append(row['rpi_bearing'] + average_drift + compass_vehicle_alignment_error)
            else:
              new_position = calculate_new_coordinates(new_lat, new_lon, row['rpi_bearing'] + compass_vehicle_alignment_error, row['rpi_distance_from_prev_coord_meters'] * doppler_compensation_factor)
              experimental_heading_array.append(row['rpi_bearing'] + compass_vehicle_alignment_error)
            new_lat = new_position['lat']
            new_lon = new_position['lon']
            
            
            experimental_lat.append(new_lat)
            experimental_lon.append(new_lon)
            average_drift_array.append(average_drift)
            average_distance_array.append(average_distance_between_rpi_and_gps)
            doppler_compensation_factor_array.append(doppler_compensation_factor)
            
          coordinates['experimental_lat'] = experimental_lat
          coordinates['experimental_lon'] = experimental_lon
          coordinates['experimental_heading'] = experimental_heading_array
          coordinates['average_drift'] = average_drift_array
          coordinates['doppler_compensation_factor'] = doppler_compensation_factor_array
          coordinates['average_distance_between_rpi_and_gps'] = average_distance_array
          
          plot_coordinates_on_mapbox(coordinates, root + '/' + folder + '/' + 'rpi-map-' + folder + '.html')
          coordinates.to_csv(root + '/' + folder + '/' + 'rpi-coordinates-analyzed-' + folder + '.csv', index=False)
        except:
          print(sys.exc_info(), root + '/' + folder + '/')

if __name__ == '__main__':
  open_path = "/home/pi/MSRS-RPI/logs"
  save_path = "/home/pi/MSRS-RPI/logs"
  calculate_drift(open_path, save_path)