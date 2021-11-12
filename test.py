from turfpy import measurement
from geojson import Point, Feature

def get_turf_distance(lat1, lat2, lon1, lon2):
  start = Feature(geometry=Point((lon1, lat1)))
  end = Feature(geometry=Point((lon2, lat2)))
  dist = measurement.distance(start,end)
  return dist

print(get_turf_distance(38.8027247, 38.7997920649094, -77.0707354, -77.074063879149)*1000)