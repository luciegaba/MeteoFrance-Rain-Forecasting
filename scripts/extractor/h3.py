from h3 import h3
import pandas as pd
import json
import plotly.graph_objects as go

class H3Processor:
    """
    This class contains methods to process data using H3 hexagons.

    Parameters:
    - hex_size (int): the size of the hexagons to use for H3 operations (default=3)
    Attributes:
    - hex_size (int): the size of the hexagons to use for H3 operations

    Methods:
    - get_h3_components(df): creates a new dataframe containing H3 hexagon IDs and their neighbors for each point in the input dataframe
    - get_geojson_from_h3(df): creates a GeoJSON object from a dataframe containing H3 hexagon IDs and their geometries
    - add_h3_neighbor_precipitation(df): adds precipitation data from neighboring hexagons to each hexagon in the input dataframe
    """

    def __init__(self, hex_size=3):
        self.hex_size = hex_size

    def get_h3_components(self, df):
        """
        Cette méthode prend en entrée un DataFrame contenant des données géographiques (latitude/longitude) et retourne un nouveau DataFrame contenant les identifiants de chaque hexagone H3 pour chaque point ainsi que les identifiants de chaque hexagone H3 voisin pour chaque point.
        
        Parameters :
        df (pandas.DataFrame) : le DataFrame d'entrée contenant les données géographiques.
        Returns :
        json_hex_ids (pandas.DataFrame) : le nouveau DataFrame contenant les identifiants de chaque hexagone H3 pour chaque point ainsi que les identifiants de chaque hexagone H3 voisin pour chaque point.
        """
        df['h3_hex_id'] = df.apply(lambda row: h3.geo_to_h3(row['lat'], row['lon'], self.hex_size), axis=1)
        df['h3_hex_id_neighbor'] = df.apply(lambda row: h3.k_ring(row['h3_hex_id']), axis=1)

        df["h3_hex_id_neighbor"] = df["h3_hex_id_neighbor"].apply(lambda x: list(x))
        neighbors = df["h3_hex_id_neighbor"].apply(pd.Series)
        df.drop(columns=["h3_hex_id_neighbor"])
        neighbors = neighbors.add_prefix('h3_hex_id_neighbor_')
        neighbors = neighbors.iloc[:, 0:3]
        df['geometry'] = df['h3_hex_id'].apply(lambda x: {"type": "Polygon",
                                                           "coordinates": [h3.h3_to_geo_boundary(x, geo_json=True)]})
        json_hex_ids = pd.concat([df, neighbors], axis=1)
        return json_hex_ids

    def get_geojson_from_h3(self, df):
        """
        Cette méthode prend en entrée un dataframe contenant des identifiants de polygones H3 et leurs géométries, et retourne un objet GeoJSON représentant les données.

        Parameters:
        df (pandas.DataFrame): le dataframe d'entrée contenant les identifiants de polygones H3 et leurs géométries
        Returns:
        geojson_dict (dict): l'objet GeoJSON représentant les données
        """
        features = []
        for i, row in df.iterrows():
            feature = {"type": "Feature",
                       "geometry": row['geometry'],
                       "properties": {"h3_hex_id": row['h3_hex_id']}}
            features.append(feature)
        feature_collection = {"type": "FeatureCollection", "features": features}

        geojson_str = json.dumps(feature_collection)
        geojson_dict = json.loads(geojson_str)
        with open('data/extras/h3.json', 'w') as outfile:
            json.dump(geojson_dict, outfile)
        return geojson_dict


    def add_h3_neighbor_precipitation(self, df):
        """
        Ajoute la précipitation pour chaque hexagone H3 à partir d'un dataframe contenant les données de précipitation.
        Les données de précipitation des voisins sont également ajoutées à chaque hexagone.

        Parameters:
        - precipitation_df (pandas.DataFrame): le dataframe contenant les données de précipitation

        Returns:
        - h3_precipitation (pandas.DataFrame): le dataframe contenant les identifiants H3 pour chaque point, 
        les identifiants H3 des voisins pour chaque point et les données de précipitation pour chaque point et chaque voisin.
        """
        temp_data=df.copy()
        for i in range(self.hex_size):
            neighbor_hex_column =   "h3_hex_id_neighbor_" + str(i)
            neighbor_df=temp_data[["h3_hex_id_neighbor_"+str(i),"date"]]
            values_for_neighbors=temp_data[["h3_hex_id","date","precip"]].rename(columns={"h3_hex_id":neighbor_hex_column})
            neighbor=pd.merge(neighbor_df,values_for_neighbors,on=["date",neighbor_hex_column])[["precip"]].rename(columns={"precip":f"h3_hex_id_neighbor_{i}_precip"})
            df=pd.concat([df,neighbor],axis=1)
            df[f"h3_hex_id_neighbor_{i}_precip"] = df.apply(lambda row: row["precip"] if pd.isna(row[f"h3_hex_id_neighbor_{i}_precip"]) else row[f"h3_hex_id_neighbor_{i}_precip"],axis=1)
        return df
    
    def plot_hexagons_on_mapbox(self, df, color='red'):
        """
        Cette méthode génère un graphique de type Scattermapbox avec des hexagones H3 et des stations météorologiques.

        Parameters:
            df (DataFrame): Le DataFrame contenant les données des stations météorologiques.
            hex_resolution (int): La résolution des hexagones H3 à afficher.
            color (str): La couleur des hexagones H3.

        Returns:
            None: Affiche le graphique interactif.
        """
        stations=df.copy()
        stations=self.get_h3_components(stations)
        hexagons = stations['h3_hex_id'].unique().tolist()

        hexagon_features = []
        for hex in hexagons:
            polygon = h3.h3_to_geo_boundary(hex, geo_json=True)
            hexagon_feature = {"type": "Feature",
                            "geometry": {"type": "Polygon", "coordinates": [polygon]}}
            hexagon_features.append(hexagon_feature)

        hexagon_collection = {"type": "FeatureCollection", "features": hexagon_features}

        hexagon_traces = []
        for feature in hexagon_collection['features']:
            trace = go.Scattermapbox(
                lat=[feature['geometry']['coordinates'][0][i][1] for i in range(7)],
                lon=[feature['geometry']['coordinates'][0][i][0] for i in range(7)],
                mode='lines',
                line=dict(width=1, color=color),
                fill='none',
                showlegend=False,
                hoverinfo='none')
            hexagon_traces.append(trace)

        station_trace = go.Scattermapbox(
            lat=stations['lat'],
            lon=stations['lon'],
            mode='markers',
            showlegend=False,
            marker=dict(size=3, color='black', opacity=0.5),
            hoverinfo='text',
            text=stations['number_sta'])

        layout = go.Layout(mapbox_style="open-street-map",mapbox_zoom=4,  # Set the initial zoom level
            mapbox_center={"lat": stations['lat'].mean(), "lon": stations['lon'].mean()})

        fig = go.Figure(data=hexagon_traces + [station_trace], layout=layout)

        fig.show()
