import pandas as pd
import regex as re
import os
import plotly.express as px
import math

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

def plot_coordinates_on_mapbox(df, save_path):
    """
    Function to plot coordinates on a mapbox map.
    """
    fig = px.scatter_mapbox(df, lat='derived_location_msrs_lat', lon='derived_location_msrs_lng', size=(df.derived_location_gps_lat/10)+1, size_max=8, color=df.sensors_imu_ins_sensor_timeOfWeek, zoom=18, center={'lat': 38.8319943, 'lon': -77.0496118}, hover_data=['derived_location_gps_lat', 'derived_location_gps_lng', 'velocity'])
    fig.update_layout(mapbox_style="dark", mapbox_accesstoken='pk.eyJ1IjoiZnJzdHlsc2tpZXIiLCJhIjoiY2tmdDFveTI5MGxraDJxdHMzYXM4OXFiciJ9.96hyKcaRFBFzH6xcsN3CYQ')
    fig.write_html(save_path.replace('.csv', '.html'))

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
    

def iterate_through_files_in_folder(folder_path):
    """
    Function to iterate through all files in a folder and return a list of
    dataframes.
    """
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            df = import_csv_as_df(folder_path + '/' + file)
            new_df = regex_column_names(df)
            for column in new_df.columns:
                if column == 'derived_location_msrs_lng':
                    plot_coordinates_on_mapbox(new_df, folder_path + '/' + file)
                elif column == 'sensor_value_usbctr4_distance':
                    plot_data_in_plotly_bar_chart(new_df, folder_path + '/' + file)
            save_csv(new_df, folder_path + '/' + file)


if __name__ == "__main__":
    path = "/Users/andrewhumphrey/Desktop/MSRS_Logs"
    iterate_through_files_in_folder(path)