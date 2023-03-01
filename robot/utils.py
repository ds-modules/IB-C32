import pandas as pd, numpy as np, seaborn as sns, matplotlib.pyplot as plt
from datascience import *
from IPython.display import *
import ipywidgets as widgets


def clean(tbl):
    df = strip(tbl.to_df())
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

def play_video(name : str) -> Video:
    if name == "sheet":
        h = 400
    else:
        h = 600
    return Video(f"videos/{name}_csv.mov", width=600, height=h, html_attributes="loop autoplay")


def feedback_button() -> None:
    button = '''
    <style>
    .button {
        border: 0;
        padding: 16px 32px 16px 32px;
        text-align: center;
        font-size: 18px;
        display: flex;
        transition: color 5s, 
                    background 5s, 
                    box-shadow 1s ease-out;
        cursor: pointer;
        color: #003262;
        border-radius: 30px;
        margin: 10% auto;
        background: linear-gradient(145deg, #e2e2e2, #bebebe);
        box-shadow: 20px 20px 40px 10px #afafaf, 
                    -20px -20px 40px 10px #f7f7f7, 
                    inset 0 0 0px, 
                    inset 0 0 0px;
    }
    
    .button:hover {
        color: #D3D3D3;
        background: #003262;
        box-shadow: 0 0 0px #000000, 
                    0 0 0px #000000, 
                    inset 20px 20px 40px 10px #002a51, 
                    inset -20px -20px 40px 10px #003b73;
    }
    </style>

    <a href="https://forms.gle/hipxf2uFw5Ud4Hyn8">
        <button class="button">
            Fill out the feedback form here
        </button>
    </a>
    '''
    display(HTML(button))