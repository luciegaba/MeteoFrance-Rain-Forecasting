import plotly.figure_factory as ff
import pandas as pd
import plotly.express as px

class WeatherVisualizations:
    """
    Une classe pour créer différentes visualisations météo en utilisant Plotly Express.

    Attributes:
    df (pd.DataFrame): Un DataFrame contenant les données météo.
    indicateurs (list): Une liste de chaînes de caractères représentant les indicateurs météo à visualiser.
    date_col (str): Le nom de la colonne contenant les dates dans le DataFrame.
    freq_map (dict): Un dictionnaire qui mappe les fréquences ("jour", "semaine", "mois", "année") aux fréquences de pandas.

    Methods:
    
    aggregate_data(self, df, freq)
        Agrège les données météo en utilisant une fréquence donnée.

    plot_data(self, freq, indicateurs, all=False)
        Trace une série temporelle pour chaque indicateur météo en utilisant une fréquence donnée.

    create_frequency_subplots(self, indicateurs, all=False)
        Trace un sous-tracé pour chaque fréquence pour chaque indicateur météo.

    plot_correlation_heatmap(self)
        Trace une heatmap de la corrélation entre les indicateurs météo.

    plot_indicators(self)
        Trace un scatter plot pour chaque indicateur météo agrégé par jour.
    """
    def __init__(self, df, indicators=['precip', 'td', 'hu', 'dd', 'psl', 'ff', 'h3_hex_id_neighbor_0_precip', 'h3_hex_id_neighbor_1_precip', 'h3_hex_id_neighbor_2_precip']):
        self.data = df.copy()
        self.indicators = indicators
        self.date_col = "date"
        self.freq_map = {'jour': 'D', 'semaine': 'W', 'mois': 'M', 'année': 'Y'}

    def aggregate_data(self, df, freq):
        data = df.copy()
        data["date"] = pd.to_datetime(data["date"])
        return data.groupby(pd.Grouper(key=self.date_col, freq=freq)).mean().reset_index()

    def plot_data(self, freq, indicators, all=False):

        if all:
            title = f"Série agrégée par {freq}"
            color_col = None
            agg_data = self.aggregate_data(self.data, self.freq_map[freq])
        else:
            title = f"Série par hexagone - {freq}"
            color_col = "h3_hex_id"
            agg_data = self.data.groupby([color_col, pd.Grouper(key=self.date_col, freq=self.freq_map[freq])]).mean().reset_index()

        for indicator in indicators:
            fig = px.line(agg_data, x="date", y=indicator, color=color_col, title=title)
            fig.show()

    def create_frequency_subplots(self, indicators, all=False):
        freqs = ["jour", "semaine", "mois", "année"]
        for freq in freqs:
            self.plot_data(freq, indicators, all)

    def plot_correlation_heatmap(self):

        correlation_matrix =  self.aggregate_data(self.data, self.freq_map["jour"])[self.indicators].corr()

        fig = ff.create_annotated_heatmap(
            z=correlation_matrix.values,
            x=self.indicators,
            y=self.indicators,
            annotation_text=correlation_matrix.round(2).values,
            colorscale='YlOrRd',
            showscale=True
        )

        fig.update_layout(
            title='Heatmap de la corrélation entre les variables',
            xaxis={'side': 'bottom'},
            width=800,
            height=800
        )

        fig.show()

    def plot_indicators(self):
         self.aggregate_data(self.data, self.freq_map["jour"])[self.indicators].plot(marker='.', alpha=0.5, linestyle='None', figsize=(11, 9), subplots=True)
