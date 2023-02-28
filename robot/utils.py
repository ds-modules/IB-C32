import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt
from datascience import *
from IPython.display import *
from ipywidgets import *


def clean(fn):
    df = strip(fn.to_df())
    # sort to forward fill with related values
    # currently sorting on index 1, but whichever has the highest correlation should be sorted
    result = df.sort_values(by=df.columns[1]).fillna(method="ffill").astype("float").astype({"Team Number" : "int"}).sort_values(by=df.columns[0]).iloc[:, :6]
    to_data_sci = Table.from_df(result)
    return to_data_sci
    

def strip(df):
    pat = r"[^.\d]*"
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.replace(pat, "", regex = True)
            empty = df[col] == ""
            df.loc[empty, col] = np.nan
    return df