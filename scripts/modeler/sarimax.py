import numpy as np
import pandas as pd
import pickle
import statsmodels.api as sm
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error
from scripts.modeler.dataset import MLDataSet
class SARIMAXCustomModel:
    """
    Classe SARIMAXCustomModel pour l'entraînement et la prédiction d'un modèle SARIMAX avec la suppression des variables non significatives.

    Attributs:
        model : Modèle SARIMAX entraîné
        sorted_columns : Liste triée des colonnes de caractéristiques
        sarimax_models (dict): un dictionnaire contenant les paramètres des modèles SARIMAX formés pour chaque hexagone.
        sarimax_models_mae (dict): un dictionnaire contenant la MAE (Mean Absolute Error) des prévisions de chaque modèle SARIMAX pour chaque hexagone.

    Methods:
        run_ols : Exécute un modèle OLS sur les données fournies.
        train : Entraîne un modèle OLS en supprimant les variables non significatives.
        predict_test_OOS : Prédit les valeurs de la colonne cible pour les nouvelles données fournies en utilisant une approche hors échantillon (Out of Sample).
        evaluate : Évalue le modèle en calculant l'erreur absolue moyenne (Mean Absolute Error - MAE) entre les valeurs réelles et prédites.
        plot_results : Affiche les résultats de prédiction et les valeurs réelles sur un graphique.
        run
        save_model
    """

    def __init__(self):
        self.model = None
        self.sorted_columns = None

    def run_ols(self, X, y):
        """
        Exécute un modèle OLS sur les données fournies.

        Parameters:
            X : DataFrame contenant les variables indépendantes
            y : Series contenant la variable dépendante

        Returns:
            model : Modèle OLS entraîné
            sorted_columns : Liste triée des colonnes de caractéristiques
        """
        sorted_columns = sorted(X.columns)
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        return model, sorted_columns

    def train(self, X, y, threshold=0.1):
        """
        Entraîne un modèle OLS en supprimant les variables non significatives.

        Parameters:
            X : DataFrame contenant les variables indépendantes
            y : Series contenant la variable dépendante
            threshold : Seuil de signification pour la suppression des variables (default : 0.1)
        """
        self.model, self.sorted_columns = self.run_ols(X, y)
        self.significative_columns = self.sorted_columns[:-1] # exclude target column
        p_values = self.model.pvalues[1:]
        max_p_value = p_values.max()
        while max_p_value > threshold:
            max_p_value_index = p_values.idxmax()
            self.significative_columns.remove(max_p_value_index)
            self.model, self.sorted_columns = self.run_ols(X[self.significative_columns], y)
            p_values = self.model.pvalues[1:]
            max_p_value = p_values.max()
            
            
    def predict_test_OOS(self, X_test, y_test, predicted_y_init):
        """
        Prédit les valeurs de la colonne cible pour les nouvelles données fournies en utilisant une approche hors échantillon (Out of Sample).

        Paramètres:
            X_test : DataFrame contenant les variables indépendantes pour le test
            y_test : Series contenant la variable dépendante pour le test
            predicted_y_init : Valeur initiale de la prédiction (généralement la dernière valeur d'entraînement)

        Retourne:
            predicted_data : DataFrame contenant les dates et les valeurs prédites
        """
        y_pred = []
        for i in range(len(X_test)):
            X_test_i = X_test.iloc[[i]]
            X_test_i.loc[:, 'precip_mean_lag_1'] = predicted_y_init
            if i > 0:
                X_test_i.loc[:, 'precip_mean_lag_2'] = y_pred[i-1]
            if i > 1:
                X_test_i.loc[:, 'precip_mean_lag_3'] = y_pred[i-2]
            if i > 2:
                X_test_i.loc[:, 'precip_mean_lag_4'] = y_pred[i-3]
            if i > 3:
                X_test_i.loc[:, 'precip_mean_lag_5'] = y_pred[i-4]
            if i > 4:
                X_test_i.loc[:, 'precip_mean_lag_6'] = y_pred[i-5]

            X_test_i = X_test_i[sorted(self.significative_columns)]
            X_test_i.insert(0, 'const', 1)
            y_i = np.dot(X_test_i,self.model.params)
            y_pred.append(y_i[0])
            predicted_y_init = y_i[0]

        predicted_data = pd.DataFrame({'Date': y_test.index, 'precip_mean_predicted': y_pred})
        predicted_data.set_index('Date', inplace=True)
        return predicted_data
    
    def evaluate(self, y_true, y_pred):
        """
        Évalue le modèle en calculant l'erreur absolue moyenne (Mean Absolute Error - MAE) entre les valeurs réelles et prédites.

        Parameters:
            y_true : Series ou liste contenant les valeurs réelles
            y_pred : Series ou liste contenant les valeurs prédites

        Returns:
            mae : Erreur absolue moyenne entre les valeurs réelles et prédites
        """
        mae = mean_absolute_error(y_true,y_pred)
        return mae

    def plot_results(self, y_true, y_pred, title, xaxis_title='Jours', yaxis_title='Pluviométrie'):
        """
        Affiche les résultats de prédiction et les valeurs réelles sur un graphique.

        Parameters:
            y_true : Series ou liste contenant les valeurs réelles
            y_pred : Series ou liste contenant les valeurs prédites
            title : Titre du graphique
            xaxis_title : Titre de l'axe des abscisses (default : 'Jours')
            yaxis_title : Titre de l'axe des ordonnées (default : 'Pluviométrie')
        """
        mae = self.evaluate(y_true, y_pred)
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=y_true, mode='lines', name='True Values', line=dict(color='red')))
        fig.add_trace(go.Scatter(y=y_pred, mode='lines', name='Predicted Values', line=dict(color='blue')))

        fig.update_layout(
            xaxis_title=xaxis_title,
            yaxis_title=yaxis_title,
            title=title,
        )
        fig.add_annotation(
            x=0.5,
            y=1.05,
            xref='paper',
            yref='paper',
            text="Mean Absolute Error: {:.4f}".format(mae),
            showarrow=False,
            font=dict(size=14)
        )
        fig.show()
    
    def run(self, data_for_arima,hexagones):

        """
        Forme des modèles SARIMAX personnalisés pour chaque hexagone dans une liste donnée, en utilisant les données de séries chronologiques fournies.

        Parameters:
            data_for_arima (DataFrame): un DataFrame contenant les données de séries chronologiques à utiliser pour l'entraînement des modèles SARIMAX.
            hexagones (list): une liste des identifiants uniques des hexagones pour lesquels des modèles doivent être formés.

        Returns:
            dict: un dictionnaire contenant les paramètres des modèles SARIMAX formés pour chaque hexagone.
        """
        self.sarimax_models = {}
        self.sarimax_models_mae = {}

        for hex_fr in hexagones:
            data_for_arima_sample = data_for_arima[data_for_arima['h3_hex_id'] == hex_fr]
            y = self.y
            instances = self.instances

            timeseries_dataset = MLDataSet(data_for_arima_sample, instances, y)
            X_train, X_test, y_train, y_test = timeseries_dataset.prepare_data()
            predicted_y_init = y_train.iloc[-1]
            model = SARIMAXCustomModel()
            model.train(X_train, y_train)
            predictions = model.predict_test_OOS(X_test, y_test, predicted_y_init)
            self.sarimax_models[hex_fr] = model.model.params
            self.sarimax_models_mae[hex_fr] = model.evaluate(y_test, predictions)
            return self.sarimax_models
        
    def save_model(self,filename='sarimax_models.pkl'):
        """
        Sauvegarde les paramètres des modèles SARIMAX formés pour chaque hexagone dans un fichier pickle.

        Parameters:
            filename (str): le nom du fichier dans lequel sauvegarder les paramètres des modèles SARIMAX.

        Returns:
            None
        """
        with open(filename, 'wb') as file:
            pickle.dump(self.sarimax_models, file)
