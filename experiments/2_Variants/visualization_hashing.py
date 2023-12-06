import math

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import sem, t
import numpy as np
from scipy import mean
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING

def sns_settings(legend  = True, legend_position = "upper center", size_reducer = 0):
    ax = plt.gca()
    if legend:
        plt.legend(loc=legend_position,fontsize=14-size_reducer)
    ax.set_xlabel(ax.get_xlabel(), fontsize=16-size_reducer)
    ax.set_ylabel(ax.get_ylabel(), fontsize=16-size_reducer)
    plt.xticks(rotation=0,fontsize = 14-size_reducer)
    plt.yticks(rotation=0, fontsize=14-size_reducer)
    plt.tight_layout()

#sns.color_palette("tab10")
sns.set_theme()
figsize = (8,5)

df = pd.read_csv("hashing_validation_results.csv")
#df2 = pd.read_csv("computationtime_results_after_P2P.csv")
#df = df.append(df2, ignore_index=True)
print(df.columns)
print(df.head())
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Extraction Technique"] = df.apply(lambda x: x["Extraction Technique"] +" "+x["Type"] if isinstance(x["Type"],str) else x["Extraction Technique"],axis =1)
for log in df["Log"].unique():
    #for technique in df[df["Log"]==log]["Extraction Technique"].unique():
    plt.figure(figsize=figsize)
    plot_df = df[(df["Log"] == log)]# & (df["Extraction Technique"] == technique)]
    sns.scatterplot(plot_df,x="Number of Process Executions",y="Computation Time", hue = "Hashing Function", style = "Extraction Technique")
    plt.show()