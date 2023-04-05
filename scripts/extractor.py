import os
import importlib
import pandas as pd
import requests


def load_data(data_path):
    final_dataframe = pd.DataFrame()
    list_files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith('.csv')]
    for file in list_files:
        final_dataframe = pd.concat([final_dataframe, pd.read_csv(file, encoding='utf-8')], axis=0)
    return final_dataframe


def get_department(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    response = requests.get(url).json()
    dep = response.get("address", {}).get("county")
    return dep

def filter_stations_by_years(data, years):
    yearly_data = {}
    common_stations = set()
    for year in years:
        yearly_data[year] = data[data["date"].dt.year == year]
        station_numbers = set(yearly_data[year]["number_sta"])
        
        if not common_stations:
            common_stations = station_numbers
        else:
            common_stations = common_stations.intersection(station_numbers)

    # Filtrer les données pour conserver uniquement les stations communes
    filtered_data = data[data['number_sta'].isin(common_stations)]

    return filtered_data

