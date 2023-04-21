import random
import pandas as pd

class MLDataSet:
    """
    Classe pour la préparation des données de séries temporelles.
    
    Attributs:
        data_for_arima (pd.DataFrame) : Données pour le modèle ARIMA.
        instances (int) : Nombre d'instances de données.
        y (pd.Series) : Valeurs cibles pour les séries temporelles.
    """

    def __init__(self, data, instances, y):
        self.data = data
        self.instances = instances
        self.y = y

    def prepare_data(self,):
        """
        Prépare les données en choisissant une série aléatoire et en la divisant en ensembles d'entraînement et de test.
        
        Returns:
            train (pd.DataFrame) : Données d'entraînement.
            test (pd.DataFrame) : Données de test.
        """
        data_for_arima_sample = self.data
        data_for_arima_sample = data_for_arima_sample.drop(columns=["h3_hex_id"])
        
        self.end_train_index = data_for_arima_sample[data_for_arima_sample['date'] == (data_for_arima_sample['date'].max() + pd.DateOffset(days=-7))].index[0]
        self.end_test_index = data_for_arima_sample.index[-1]
        self.X = data_for_arima_sample[self.instances]
        self.y = data_for_arima_sample[self.y]
        self.X_train, self.X_test,self.y_train,self.y_test = self.train_test_split(self.X,self.y, end_train_index=self.end_train_index)
        
        return self.X_train, self.X_test,self.y_train,self.y_test

    def train_test_split(self, X,y=None, end_train_index=0.2):
        """
        Divise les données en ensembles d'entraînement et de test en fonction de l'indice de fin d'entraînement.
        
        Paramètres:
            X (pd.DataFrame) : Données à diviser.
            y (pd.Series): target à diviser (optionnelle on peut mettre un dataset entier)
            end_train_index (int) : Indice de fin de l'ensemble d'entraînement/ratio
            
        Retourne:
            X_train (pd.DataFrame) : Données d'entraînement.
            X_test (pd.DataFrame) : Données de test.
        """
        if end_train_index<1:
            end_train_index = int(len(X) * (1 - end_train_index))
        X_train, X_test = X.loc[:end_train_index], X.loc[end_train_index+1:] 
        print('Échantillons d\'entraînement:', len(X_train))
        print('Échantillons de test:', len(X_test))
        if y is not None:
            y_train,y_test = y.loc[:end_train_index], y.loc[end_train_index+1:] 
            return X_train,X_test,y_train,y_test
        else:
            return X_train, X_test