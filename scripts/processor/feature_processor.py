import pandas as pd
class FeaturesConstructor:   
    """
    Classe DataTransformer pour transformer les données météorologiques par jour pour chaque hexagone H3.
    Cette classe effectue les étapes d'agrégation et d'ajout des colonnes pour la saison (haute ou basse) et les mois sous forme de one-hot encoding.
    """
    def __init__(self):
        self.y = "precip_mean"

    def aggregate_data_by_day(self, data):
        """
        Agrège les données par jour pour chaque hexagone H3.
        
        Parameters:
        - data (pandas.DataFrame): les données à agréger
        
        Returns:
        - grouped_df (pandas.DataFrame): les données agrégées par jour pour chaque hexagone H3
        """
        
        self.agg_methods = {
            'dd': 'mean',
            'ff': 'mean',
            'precip': ['min','max', 'mean'],
            'hu': 'mean',
            't':'mean',
            'td': 'mean',
            'h3_hex_id_neighbor_0_precip':'mean', 
            'h3_hex_id_neighbor_1_precip':'mean', 
            'h3_hex_id_neighbor_2_precip':'mean'
        }
        
        self.features = list(self.agg_methods.keys())
        data['date'] = pd.to_datetime(data['date'])
        data['date'] = data['date'].dt.date
        grouped_df = data.groupby(['h3_hex_id', 'date']).agg(self.agg_methods).reset_index()

        grouped_df.columns = ['_'.join(col) if col[1] else col[0] for col in grouped_df.columns]
        grouped_df["precip_max_min"] = grouped_df["precip_max"] - grouped_df["precip_min"]
        grouped_df.drop(columns=["precip_min","precip_max"], inplace=True)
        self.features = [col for col in grouped_df.columns.tolist() if (col != "h3_hex_id") and (col !="date") and (col!="precip_mean") ]

        for column in self.features:
            grouped_df[column] = grouped_df.groupby('h3_hex_id')[column].transform(lambda x: x.fillna(method="bfill"))

        grouped_df["date"] = pd.to_datetime(grouped_df['date'])
        

        return grouped_df

    def create_saison_month_columns(self, aggregate_data):
        """
        Ajoute des colonnes pour la saison (haute ou basse) et les mois sous forme de one-hot encoding.
        
        Parameters:
        - aggregate_data (pandas.DataFrame): les données agrégées
        
        Returns:
        - aggregate_data (pandas.DataFrame): les données agrégées avec les colonnes supplémentaires pour la saison et les mois
        """
        def saison(row):
            if row in [1, 2, 3, 10, 11, 12]:
                return 0
            elif row in [4, 5, 6, 7, 8, 9]:
                return 1
            else:
                return None

        aggregate_data['month'] = aggregate_data['date'].dt.month
        aggregate_data['saison_haute_basse'] = aggregate_data["month"].apply(saison)
        one_hot_month = pd.get_dummies(aggregate_data['month'], prefix='Month')
        aggregate_data = pd.concat([aggregate_data.drop(columns=["month"]), one_hot_month], axis=1)

        return aggregate_data
    

    def compute_var_lagged(self,df,nb_lag_var,nb_lag_exo):

        """
        Calcul les variables retardées pour la/les variable/s
        """
        
        self.nb_lag_var = nb_lag_var
        self.nb_lag_exo = nb_lag_exo
        
        df_lags = df.copy()
        df_lags_exo = df_lags[self.features]
        df_lags_y = df_lags[[self.y]]
        df_others = df_lags.drop(columns=self.features+[self.y]) 


        for col in df_lags_exo.columns:
            for lag in range(1, nb_lag_exo+1):
                df_lags_exo[col+"_lag_"+str(lag)] = df_lags_exo[col].shift(lag)
        
        for lag in range(1, nb_lag_var+1):
            df_lags_y[self.y+"_lag_"+str(lag)] = df_lags_y[self.y].shift(lag)
        
        
        return pd.concat([df_lags_y,df_lags_exo,df_others],axis=1)
    

    def run(self, data, post_ts=True, nb_lag_var=1, nb_lag_exo=1):
        """Pipeline qui lance l'ensemble des différentes étapes d'agrégation +features issus de l'analyse en séries temporelles si post_ts est True

        Args:
            data (pd.DataFrame): les données à agréger
            post_ts (bool, optional): features issus de l'étude séries temporelles (indicatrices mois/saison, variables retardées). Defaults to True.
            nb_lag_var (int, optional): nombre de lags pour y. 
            nb_lag_exo (int, optional): nombre de lags pour variables exogènes

        Returns:
            processed_data: DataFrame processé
        """
        aggregated_data = self.aggregate_data_by_day(data)
        if post_ts is True:
            transformed_data = self.create_saison_month_columns(aggregated_data)
            lagged_data = self.compute_var_lagged(transformed_data, nb_lag_var, nb_lag_exo)
            lagged_data.drop(self.features, axis=1, inplace=True)
            lagged_data.dropna(inplace=True)
            self.instances = [feature for feature in lagged_data.columns.tolist() if (feature != self.y) and (feature !="date") and (feature !="h3_hex_id")]
            self.processed_data = lagged_data
        else:
            self.processed_data = aggregated_data
            self.instances = [feature for feature in self.processed_data.columns.tolist() if (feature != self.y) and (feature !="date") and (feature !="h3_hex_id")]

        return self.processed_data
    
  