import plotly.graph_objects as go
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Flatten
import plotly.graph_objects as go
from sklearn.metrics import mean_absolute_error

class LSTMModel:
    """
    Classe permettant de créer et entraîner un modèle LSTM pour la prédiction de séries chronologiques.

    Parameters:
        data (DataFrame): Les données d'entraînement utilisées pour créer et entraîner le modèle LSTM.
        target_column (str): Le nom de la colonne cible à prédire.
        time_steps (int): Le nombre de pas de temps pour prédire la valeur de la colonne cible.

    Attributes:
        data (DataFrame): Les données d'entraînement utilisées pour créer et entraîner le modèle LSTM.
        target_column (str): Le nom de la colonne cible à prédire.
        time_steps (int): Le nombre de pas de temps pour prédire la valeur de la colonne cible.
        model (Sequential): L'architecture du modèle LSTM.
        
    Methods:
    prepare_data: Prépare les données pour l'entraînement et la prédiction.
    train_test_split: Divise les données en ensembles d'entraînement et de test.
    create_model: Crée l'architecture du modèle LSTM.
    train: Entraîne le modèle LSTM sur les données d'entraînement.
    predict_OOS: Prédit les valeurs de la colonne cible en utilisant la prévision dynamique (out-of-sample).
    evaluate: Évalue les performances du modèle en utilisant l'erreur absolue moyenne (MAE).
    plot_results: Affiche un graphique des valeurs réelles et prédites.
    run: Crée et entraîne des modèles LSTM pour chaque hexagone dans une liste donnée, en utilisant les données de séries chronologiques fournies.
    save_models
    """

    def __init__(self, data, target_column, time_steps=5):
        self.data = data
        self.target_column = target_column
        self.time_steps = time_steps
        self.model = None

    def prepare_data(self):
        num_features = len(self.data.columns)
        data_3d = np.array([self.data[i:i+self.time_steps].values for i in range(len(self.data) - self.time_steps)])

        X = data_3d
        y = self.data[self.target_column][self.time_steps:]

        return X, y

    def train_test_split(self, X, y=None, end_train_index=0.8):
        if end_train_index < 1:
            end_train_index = int(len(X) * end_train_index)
        X_train, X_test = X[:end_train_index], X[end_train_index:]
        print("Échantillons d'entraînement:", len(X_train))
        print("Échantillons de test:", len(X_test))

        if y is not None:
            y_train, y_test = y[:end_train_index], y[end_train_index:]
            return X_train, X_test, y_train, y_test
        else:
            return X_train, X_test

    def create_model(self, num_features, units=64, activation='relu', loss="mse", optimizer="adam"):
        model = Sequential()
        model.add(LSTM(units=units, activation=activation, input_shape=(self.time_steps, num_features)))
        model.add(Flatten())
        model.add(Dense(1,activation=activation))
        model.compile(optimizer=optimizer, loss=loss)
        return model

    def train(self, X_train, y_train,X_valid,y_valid, epochs=50, verbose=2, units=64, activation='relu', loss="mse", optimizer="adam"):
        self.model = self.create_model(X_train.shape[2], units, activation, loss, optimizer)
        self.model.fit(X_train, y_train, validation_data=(X_valid,y_valid), epochs=epochs, verbose=verbose)

    def predict_OOS(self,X_test):
        Y_pred = []
        for i in range(len(X_test)):
                input_data = X_test[i].reshape(1, X_test.shape[1], X_test.shape[2])
                pred = self.model.predict(input_data)[0][0]
                Y_pred.append(pred)
                if i + 1 < len(X_test):
                    X_test[i + 1][0][0] = pred
        return np.array(Y_pred)

    

    def evaluate(self, y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        return mae
    
    
    def plot_results(self, y_true, y_pred, title, xaxis_title='Jours', yaxis_title='Pluviométrie'):

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
        
    def run(self, data_for_deep, hexagones, units=64, activation='relu', loss="mse", optimizer="adam", epochs=50):
        self.lstm_models = {}
        self.lstm_models_mae = {}
        data = data_for_deep.copy()
        for chosen_hex_id in hexagones:
            single_data=data_for_deep[data_for_deep["h3_hex_id"]==chosen_hex_id]
            single_data.drop(columns=["h3_hex_id"], inplace=True)
            single_data.set_index("date", inplace=True)
            target_column = 'precip_mean'
            time_steps = 7
            lstm_model = LSTMModel(single_data, target_column, time_steps)
            X, y = lstm_model.prepare_data()
            end_train_date = single_data.index.max() + pd.DateOffset(days=-7)
            end_train_index = single_data[single_data.index <= end_train_date].shape[0]-7
            X_train, X_test, y_train, y_test = lstm_model.train_test_split(X, y, end_train_index)
            X_train, X_valid, y_train, y_valid = lstm_model.train_test_split(X_train, y_train, 0.8)
            lstm_model.train(X_train, y_train, X_valid, y_valid, epochs=epochs, units=units, activation=activation, loss=loss, optimizer=optimizer)
            predicted_data = lstm_model.predict_OOS(X_test)
            self.lstm_models[chosen_hex_id] = lstm_model.model
            self.lstm_models_mae[chosen_hex_id] = lstm_model.evaluate(y_test, predictions)
            return self.lstm_models
        
    def save_models(self, directory='models/lstm_models'):
        """
        Saves the trained LSTM models for each hexagon in a specified directory.

        Parameters:
            directory (str): the directory in which to save the LSTM models.

        Returns:
            None
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

        for hex_id, model in self.lstm_models.items():
            model.save(os.path.join(directory, f'lstm_model_{hex_id}.h5'))