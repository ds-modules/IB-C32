import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt
import json, re, os, math, random, warnings, scipy, pickle, time, sys, gc
from datascience import *
from IPython.display import *
from ipywidgets import *


def clean(fn):
    return strip(pd.read_csv(fn)).fillna(method="ffill").astype("float").astype({"Team Number" : "int"})
def strip(df):
    pat = r"[^.\d]*"
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.replace(pat, "", regex = True)
            empty = df[col] == ""
            df.loc[empty, col] = np.nan
    return df