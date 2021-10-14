import pandas as pd
import regex as re
import os
import plotly.express as px
import math
import shutil
import sys

def regex_column_names(df):
    """
    Function to replace all period characters in column names with
    underscores.
    """
    df.columns = [re.sub(r'\.', '_', col) for col in df.columns]
    return df

def fill_in_blank_values_in_df(df):
    """
    Function to fill in blank values in a dataframe.
    """
    df = df.fillna(0)
    return df

def write_to_file(file_path, text):
    """
    Function to write to a file.
    """
    with open(file_path, 'a') as f:
        f.write(text)
        
def delete_file(file_path):
    """
    Function to delete a file.
    """
    os.remove(file_path)

def plot_data_in_plotly_bar_chart(df, save_path):
    """
    Function to plot data in a plotly bar chart.
    """
    try:
        delete_file(save_path.replace('.csv', '.html'))
    except:
        pass
    for i in range(len(df.columns)):
        i = px.area(df, x='dt_inc', y=df.columns[i], title=df.columns[i], height=400)
        i.update_layout(title_font_color="red", title_x=0.5, title_font_size=18)
        write_to_file(save_path.replace('.csv', '.html'), i.to_html(full_html=False))

def plot_coordinates_on_mapbox(df, save_path, folder_path):
    """
    Function to plot coordinates on a mapbox map.
    """
    if not df.empty:
        try:
            fig = px.scatter_mapbox(df, lat='rpi_lat', lon='rpi_lon', zoom=18, color_discrete_sequence=['#fd6bbe'], center={'lat': df['rpi_lat'][0], 'lon': df['rpi_lon'][0]}, hover_data=["timestamp"])
            fig2 = px.scatter_mapbox(df, lat='msrs_lat', lon='msrs_lon', zoom=18, color_discrete_sequence=['blue'], hover_data=["timestamp"])
            fig3 = px.scatter_mapbox(df, lat='gps_lat_x', lon='gps_lon', zoom=18, color_discrete_sequence=['#befd05'], hover_data=["timestamp"])
            fig.add_trace(fig2.data[0])
            fig.add_trace(fig3.data[0])
            fig.update_layout(mapbox_style="dark", mapbox_accesstoken='pk.eyJ1IjoiZnJzdHlsc2tpZXIiLCJhIjoiY2tmdDFveTI5MGxraDJxdHMzYXM4OXFiciJ9.96hyKcaRFBFzH6xcsN3CYQ')
            fig.write_html(save_path.replace('.csv', '.html'))
        except:
            print(sys.exc_info(), save_path)
    else:
        shutil.rmtree(folder_path)


def import_csv_as_df(csv_file):
    """
    Function to import a csv file as a pandas dataframe.
    """
    df = pd.read_csv(csv_file)
    return df

def save_csv(df, save_path):
    """
    Function to save a dataframe as a csv file.
    """
    df.to_csv(save_path, index=False)
    
def calculate_distance_between_two_coordinates(lat1, lon1, lat2, lon2):
    """
    Function to calculate the distance between two coordinates.
    """
    R = 6373.0
    lat1 = lat1 * (3.14159265359/180)
    lon1 = lon1 * (3.14159265359/180)
    lat2 = lat2 * (3.14159265359/180)
    lon2 = lon2 * (3.14159265359/180)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance
    

def iterate_through_files_in_folder(open_path, save_path):
    """
    Function to iterate through all files in a folder and return a list of
    dataframes.
    """
    for root, subdirectories, files in os.walk(open_path):
        for folder in subdirectories:
            try:
                shutil.rmtree(os.path.join(save_path, folder))
            except:
                pass
            try:
                os.mkdir(os.path.join(save_path, folder))
            except:
                pass
            data1 = pd.read_csv(root + '/' + folder + '/' + 'rpi-coordinates.csv')
            data2 = pd.read_csv(root + '/' + folder + '/' + 'rpi-compass.csv')
            output1 = pd.merge(data1, data2, on='timestamp', how='inner')
            
            data3 = pd.read_csv(root + '/' + folder + '/' + 'rpi-imu.csv')
            data4 = pd.read_csv(root + '/' + folder + '/' + 'rpi-doppler.csv')
            output2 = pd.merge(data3, data4, on='timestamp', how='inner')
            output3 = pd.merge(output1, output2, on='timestamp', how='inner')
            
            data5 = pd.read_csv(root + '/' + folder + '/' + 'biodigital-imu.csv')
            data6 = pd.read_csv(root + '/' + folder + '/' + 'biodigital-dmc.csv')
            output4 = pd.merge(data5, data6, on='timestamp', how='inner')
            output5 = pd.merge(output3, output4, on='timestamp', how='inner')

            data7 = pd.read_csv(root + '/' + folder + '/' + 'rpi-altitude-temperature.csv')
            output6 = pd.merge(output5, data7, on='timestamp', how='inner')
            
            output6.to_csv( save_path + '/' + folder + '/' + 'master.csv', index=False, encoding='utf-8-sig')
    for root, subdirectories, files in os.walk(save_path):
        for file in files:
            if file == 'master.csv':
                df = import_csv_as_df(os.path.join(save_path, root.split('/')[-1]) + '/' + file)
                plot_coordinates_on_mapbox(df, os.path.join(save_path, root.split('/')[-1]) + '/' + file, os.path.join(save_path, root.split('/')[-1]))


if __name__ == "__main__":
    open_path = "/Volumes/pi/MSRS-RPI/logs"
    save_path = "/Users/andrewhumphrey/Desktop/exported_maps"
    iterate_through_files_in_folder(open_path, save_path)