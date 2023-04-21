from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import STL
import plotly.graph_objs as go
import plotly.express as px

class TimeSeriesPlots:
    """
    La classe TimeSeriesPlots fournit des méthodes pour créer des graphiques utiles pour l'analyse des séries temporelles.
    Elle inclut des fonctions pour afficher la décomposition STL (Saison-Tendance-Résidus) et les graphiques de la fonction d'autocorrélation (ACF) et de la fonction d'autocorrélation partielle (PACF).
    
    Attributs:
        time_series (pd.Series): une série avec en index les dates
    Methods:
        plot_stl_decomposition(period): Affiche la décomposition STL
        show_acf_pacf(lags): Affiche des graphiques de la fonction d'autocorrélation (ACF)
        plot_correlation_lags(data): Affiche un graphique de l'ensemble des corrélations au lag 1 pour chaque hexagone (pour une variable donnée)
    """
    def __init__(self, time_series):
        self.time_series = time_series

    def plot_stl_decomposition(self, period=365): 
        """
        Affiche la décomposition STL (Saison-Tendance-Résidus) de la série temporelle.
        
        Paramètres:
            period (int) : La période saisonnière de la série temporelle (par défaut 365).
        """
        stl = STL(self.time_series, period=period)
        result = stl.fit()
        trend = result.trend
        seasonal = result.seasonal
        residual = result.resid

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=self.time_series.index, y=self.time_series, mode='lines', name='Série originale'))
        fig.add_trace(go.Scatter(x=trend.index, y=trend, mode='lines', name='Tendance'))
        fig.add_trace(go.Scatter(x=seasonal.index, y=seasonal, mode='lines', name='Saisonnalité'))
        fig.add_trace(go.Scatter(x=residual.index, y=residual, mode='lines', name='Résidus'))

        fig.update_layout(title='Décomposition STL de la série temporelle',
                          xaxis_title='Date',
                          yaxis_title='Valeur')

        fig.show()

    def show_acf_pacf(self, lags=30):
        """
        Affiche les graphiques de la fonction d'autocorrélation (ACF) et de la fonction d'autocorrélation partielle (PACF) de la série temporelle.
        
        Paramètres:
            lags (int) : Le nombre de décalages (lags) à afficher dans les graphiques (par défaut 30).
        """
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

        # plot ACF on the left subplot
        plot_acf(self.time_series, lags=lags, ax=axs[0])
        axs[0].set_title("ACF of " + self.time_series.name)

        # plot PACF on the right subplot
        plot_pacf(self.time_series, lags=lags, ax=axs[1])
        axs[1].set_title("PACF of " +  self.time_series.name)

        # show the plot for each variable
        plt.show()

    def plot_correlation_lags(self,time_series_all):
        """
        Affiche un graphique montrant la corrélation entre la série de précipitations observée et
        la série retardée de 1 jour pour l'ensemble des variables
        """
        dataframe = time_series_all.copy()
        dataframe['precip_t_1'] = dataframe.groupby('h3_hex_id')['precip'].shift(1)
        dataframe.dropna(subset=['precip_t_1'], inplace=True)

        correlations = dataframe.groupby('h3_hex_id').apply(lambda x: x[['precip', 'precip_t_1']].corr().iloc[0, 1]).reset_index()
        correlations.columns = ['h3_hex_id', 'correlation']
        correlations.sort_values(by='correlation', ascending=True, inplace=True)

        fig = px.bar(correlations, x='h3_hex_id', y='correlation', text='correlation')
        fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig.update_layout(
            title="Corrélation entre les précipitations et les précipitations retardées de 1 jour",
            xaxis_title="Régions",
            yaxis_title="Corrélation",
            xaxis_tickangle=-45
        )
        fig.show()