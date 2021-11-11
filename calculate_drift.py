import os
import pandas as pd
import sys

def import_csv_as_df(csv_file):
  """
  Function to import a csv file as a pandas dataframe.
  """
  df = pd.read_csv(csv_file)
  return df

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
                print(coordinates.columns['rpi_lat'])
            except:
                print(sys.exc_info(), root + '/' + folder + '/')

if __name__ == '__main__':
  open_path = "/home/pi/MSRS-RPI/logs"
  save_path = "/home/pi/MSRS-RPI/logs"
  calculate_drift(open_path, save_path)