from statsmodels.tsa.stattools import kpss, adfuller
import pandas as pd

class TestsStationarite:
    """
    Classe qui effectue les tests de stationnarité KPSS et Augmented Dickey-Fuller (ADF) sur un DataFrame.
    """
    
    def __init__(self, df):
        self.df = df
    
    def kpss_test(self, regression, alpha='5%'):
        """
        Effectue le test KPSS sur chaque colonne de la DataFrame.
        
        Paramètres :
        - regression (str) : Type de régression ('c' pour constant, 'ct' pour constant et tendance)
        - alpha (str) : Seuil de significativité (ex: '5%')
        
        Retourne :
        - results (pd.DataFrame) : DataFrame contenant les résultats du test KPSS pour chaque colonne
        """
        results = pd.DataFrame(columns=['Test', 'Variable', 'Regression', 'Test Statistic', 'p-value', 'Lags Used', 'Résultat'])

        for col in self.df.columns:
            kpss_result = kpss(self.df[col], regression=regression)

            results.loc[len(results)] = ['KPSS', col, regression, round(kpss_result[0], 3), round(kpss_result[1], 3), kpss_result[2], kpss_result[0] < kpss_result[3][alpha]]

        results['Résultat'] = results['Résultat'].replace(False, 'Non Stationnaire')
        results['Résultat'] = results['Résultat'].replace(True, 'Stationnaire')

        return results

    def adf_test(self, regression, alpha='5%'):
        """
        Effectue le test ADF sur chaque colonne de la DataFrame.
        
        Parameters :
        - regression (str) : Type de régression ('c' pour constant, 'ct' pour constant et tendance)
        - alpha (str) : Seuil de significativité (ex: '5%')
        
        Returns :
        - results (pd.DataFrame) : DataFrame contenant les résultats du test ADF pour chaque colonne
        """
        results = pd.DataFrame(columns=['Test', 'Variable', 'Regression', 'Test Statistic', 'p-value', 'Lags Used', 'Résultat'])

        for col in self.df.columns:
            adf_result = adfuller(self.df[col], regression=regression)

            results.loc[col] = ['ADF', col, regression, round(adf_result[0], 3), round(adf_result[1], 3), adf_result[2], adf_result[1] < 0.05]

        results['Résultat'] = results['Résultat'].replace(False, 'Non Stationnaire')
        results['Résultat'] = results['Résultat'].replace(True, 'Stationnaire')

        return results

    def concat_tests_and_sort(self, kpss, adf):
        """
        Concatène les résultats des tests KPSS et ADF et les trie.
        
        Parameters :
        - kpss (pd.DataFrame) : DataFrame contenant les résultats du test KPSS
        - adf (pd.DataFrame) : DataFrame contenant les résultats du test ADF
        
        Returns :
        - results_of_tests (pd.DataFrame) : DataFrame contenant les résultats triés des deux tests
        """
        results_of_tests = pd.concat([kpss, adf], ignore_index=True)
        results_of_tests = results_of_tests.drop('Test Statistic', axis=1)
        results_of_tests = results_of_tests.sort_values(['Variable', 'Regression'], ascending=[True, False])
        return results_of_tests
    
    def execute_tests(self, regression_kpss='c', regression_adf='n', alpha='5%'):
        """
        Effectue les tests KPSS et ADF, puis concatène et trie les résultats.

        Parameters :
        - regression_kpss (str) : Paramètre de régression pour le test KPSS ('c' ou 'ct')
        - regression_adf (str) : Paramètre de régression pour le test ADF ('c', 'ct' ou 'nc')
        - alpha (str) : Niveau de signification pour les tests (par exemple '5%')

        Returns :
        - results_of_tests (pd.DataFrame) : DataFrame avec les résultats des tests concaténés et triés
        """
        kpss_results = self.kpss_test(regression_kpss, alpha)
        adf_results = self.adf_test(regression_adf, alpha)
        results_of_tests = self.concat_tests_and_sort(kpss_results, adf_results)
        return results_of_tests
   
    
def get_stationarity_results(data_for_time_series):
    """
    Calcule les résultats des tests de stationnarité (KPSS et ADF) pour chaque h3_hex_id unique dans le DataFrame fourni.

    Paramètres :
    - data_for_time_series (pd.DataFrame) : DataFrame contenant les données de séries temporelles pour lesquelles les tests de stationnarité doivent être effectués.

    Retourne :
    - stationarity_hex (pd.DataFrame) : DataFrame contenant les résultats des tests de stationnarité pour chaque h3_hex_id unique.
    """
    stationarity_hex = pd.DataFrame()
    for hex in data_for_time_series['h3_hex_id'].unique():
        serie = pd.DataFrame(data_for_time_series[data_for_time_series['h3_hex_id'] == hex]['precip_mean'])
        test_stationarite = TestsStationarite(serie)
        serie_tests = test_stationarite.execute_tests('c', 'n', '5%')
        stationarity_hex = pd.concat([stationarity_hex, serie_tests])
    return stationarity_hex    


