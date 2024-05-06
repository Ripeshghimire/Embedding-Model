import pandas as pd

global_df = pd.DataFrame()

def get_global_df():
    global global_df
    return global_df

def set_global_df(df):
    global global_df
    global_df = df