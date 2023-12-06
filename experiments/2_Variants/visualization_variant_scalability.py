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

df = pd.read_csv("computationtime_results_after_Fin.csv")
df2 = pd.read_csv("computationtime_results_after_P2P.csv")
df = df.append(df2, ignore_index=True)
print(df.columns)
print(df.head())
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Extraction Technique"] = df.apply(lambda x: x["Extraction Technique"] +" "+x["Type"] if isinstance(x["Type"],str) else x["Extraction Technique"],axis =1)
df["Computation Time"] = df["Computation Time"].replace({-1:3000})
#df = df.rename(columns = {"Mapping Time":"Distance Calculation","Clustering Time":"Inter-Variant Matching","Summarization Time":"Inter-Variant Summarization"})
for log in df["Log"].unique():
    for technique in df[df["Log"]==log]["Extraction Technique"].unique():
        plt.figure(figsize=figsize)
        plot_df = df[(df["Log"]==log) & (df["Extraction Technique"]== technique)]
        sns.lineplot(data = plot_df,x="Number of Process Executions",y="Computation Time", hue="Variant Computation")
        if len(plot_df[(plot_df["Computation Time"] == 3000)]) != 0:
            # Add a horizontal line for the timeout threshold
            plt.axhline(y=3000, color='red', linestyle='--')

            # Annotate the timeout line
            plt.text(x=plot_df['Number of Process Executions'].min(), y=3000, s=' Computation Timeout', color='red',
                     verticalalignment='bottom')
            sns.scatterplot(data=plot_df[(plot_df["Computation Time"] == 3000)], x="Number of Process Executions", y="Computation Time",color = "red", marker = "X")
        plt.ylabel('Computation Time (in s)')
        plt.title('Variant Computation Time: '+log+' Event Log and '+technique, fontsize=14)
        sns_settings(legend=True, legend_position = "center left")
        plt.show()