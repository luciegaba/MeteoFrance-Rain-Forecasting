from scipy import stats
import dask.dataframe as dd
from scripts.extractor.h3 import H3Processor
import os

class DaskDatabaseBuilder:
    """
    Classe DataPreprocessor pour le prétraitement des données météorologiques. Cette classe effectue les étapes suivantes :
    1) Récupération des différents sets de données sous forme d'un dataframe dask (load_data)
    2) Création d'un dataset comportant différentes informations sur les stations (coordonnées GPS) et attribution de repères H3
    2) Conversion de la colonne 'date' en datetime et arrondi à l'heure, puis regroupement par station et date.
    3) Fusion des données avec les informations de l'aggrégateur et les voisins.
    4) Regroupement des données en fonction des méthodes d'agrégation définies.

    Attributs:
        hex_size (int): Hexagone level pour h3
        indicators (list): Liste des indicateurs météorologiques à traiter.
        aggregator (str): Colonne utilisée pour l'agrégation des données.
        agg_methods (dict): Dictionnaire définissant les méthodes d'agrégation pour chaque colonne.
    
    Methods:
        mode(x): Calcule le mode pour l'aggrégation
        load_data(x): Récupère les données dans le repo indiqué puis concatène en un dataframe dask (pour csv)
        process_data(data,stations): Concatène les informations des stations, dont les hex_id, puis fait l'aggrégation par hex_id par heure
        export_data(filename): Exporte les données pré-traitées
    """
    def __init__(self,hex_size=3):
        self.hex_size=hex_size
        self.indicators = ["dd", "ff", "precip", "hu", "td", "t", "psl"]
        self.aggregator = "h3_hex_id"
        self.agg_methods = {
            "dd": "mean",
            "ff": "mean",
            "precip": "mean",
            "hu": "mean",
            "td": "mean",
            "t": "mean",
            "psl": "mean",
            "h3_hex_id_neighbor_0": self.mode,
            "h3_hex_id_neighbor_1": self.mode,
            "h3_hex_id_neighbor_2": self.mode,
        }

    @staticmethod
    def mode(x):
        return stats.mode(x)[0][0]

    def load_data(self,folder):
        #1) Récupère les différents sets de données sous forme d'un dataframe dask
        self.data = dd.read_csv(os.getcwd()+folder+"/*.csv", header=0)
    
    def run(self):
        # Definition h3 (cf H3Processor pour plus de détails):
        h3_processor = H3Processor(self.hex_size)
        # 1) Récupère les caractéristiques des stations + les caractéristiques H3 (voisins,id, coordonnées,etc...)
        self.stations = self.data[["number_sta","lat","lon","height_sta"]].drop_duplicates(subset="number_sta").compute()
        self.stations_post_h3=h3_processor.get_h3_components(self.stations)
        # 2) Convertir la colonne 'date' en datetime et arrondir à l'heure + groupby par station/date
        self.data["date"] = dd.to_datetime(self.data["date"], format="%Y%m%d %H:%M").dt.round("H")
        data_grouped_by_stations = self.data.groupby(["number_sta", "date"])[self.indicators].mean().reset_index().compute()
        # 3) Merge les données avec les informations de l'aggrégateur (+ les voisins)
        self.data_with_hex = dd.merge(data_grouped_by_stations, self.stations_post_h3[["number_sta", "h3_hex_id", "h3_hex_id_neighbor_0", "h3_hex_id_neighbor_1", "h3_hex_id_neighbor_2"]], how="left", on="number_sta")
        # 4) Groupby selon les méthodes définies dans la cellule précédente
        self.preprocessed_data = self.data_with_hex.groupby([self.aggregator, "date"]).agg(self.agg_methods)
        self.preprocessed_data=self.preprocessed_data.reset_index()
        # 5) Rajouter les précipitations aggrégées des hexagones voisins
        self.preprocessed_data=h3_processor.add_h3_neighbor_precipitation(self.preprocessed_data) 
        return self.preprocessed_data
    
    def export_data(self, filename):
        self.preprocessed_data.to_csv(filename, index=False)