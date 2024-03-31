import pandas as pd
from wordcloud import WordCloud 
from mysql_con import global_connection as con
import matplotlib.pyplot as plt

data_structure = {
    'int64': {
        'hist': ['mean', 'median', 'mode', 'std', 'quantile', 'skew'],
        'boxplot': ['median', 'quantile'],
        'line': ['mean', 'median'],
        'scatter': ['corr'],
        'bar': ['value_counts']
    },
    'float64': {
        'hist': ['mean', 'median', 'std', 'quantile', 'skew'],
        'boxplot': ['median', 'quantile'],
        'line': ['mean', 'median'],
        'scatter': ['corr'],
        'bar': ['value_counts']
    },
    'datetime64': {
        'line': ['mean', 'median'],
        'scatter': ['corr']
    },
    'timedelta64': {
        'hist': ['mean', 'median', 'std', 'quantile'],
        'line': ['mean', 'median']
    },
    'object': {
        'bar': ['value_counts'],
        'wordcloud': ['wordcloud']
    },
    'category': {
        'bar': ['value_counts']
    },
    'bool': {
        'bar': ['value_counts']
    }
}


def get_possible_plots(table , column):
    df = create_dataframe_from_mysql(table, column)
    data_type = df[column].dtype
    return [plot_type for data_types, data_plots in data_structure.items() if data_type in data_types for plot_type in data_plots.keys()]

def get_possible_measures(plot_type , data_type):
    return data_structure[data_type][plot_type]

def generate_plot(plot_type, measure):
    df = create_dataframe_from_mysql("etu" , "nom")
    if measure in dir(df) and callable(getattr(df, measure)):
        getattr(df, measure)().plot(kind=plot_type)
        plt.ylabel(measure)
        plt.title(f'{measure} Box Plot')
        plt.show()
    else :        
        text_data = ' '.join(df)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Word Cloud')
        plt.show()


def create_dataframe_from_mysql(table, column):
    query = f"SELECT {column} FROM {table}"
    df = pd.read_sql_query(query , con)
    return df[column]

generate_plot("wordcloud", "wordcloud")

