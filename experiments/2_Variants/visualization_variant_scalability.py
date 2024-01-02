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

sns.color_palette("tab10")
sns.set_theme(style = 'darkgrid')
figsize = (7,10)

#df = pd.read_csv("results_a_scalability_full.csv")
df = pd.read_csv("results_variants_a_cluster_p2p.csv")
df2 = pd.read_csv("results_variants_a_cluster_order.csv")
df = df.append(df2, ignore_index=True)
df2 = pd.read_csv("results_variants_a_cluster_inc.csv")
df = df.append(df2, ignore_index=True)
df2 = pd.read_csv("results_variants_a_cluster_fin.csv")
df = df.append(df2, ignore_index=True)
#print(df.columns)
#print(df.head())
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
df["Variant Computation"] = df["Variant Computation"].replace({"naive_mapping":"Object Mapping",
             "one_phase":"Projected Process Executions (PPE) and LGI",
             "two_phase":"Hashing and Validation of PPE"})
hue_order = df["Variant Computation"].unique()
print(hue_order)
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Extraction Technique"] = df.apply(lambda x: x["Extraction Technique"] +" "+x["Type"] if isinstance(x["Type"],str) else x["Extraction Technique"],axis =1)
df["Computation Time"] = df["Computation Time"].replace({-1:3000})
#df = df.rename(columns = {"Mapping Time":"Distance Calculation","Clustering Time":"Inter-Variant Matching","Summarization Time":"Inter-Variant Summarization"})
# for log in df["Log"].unique():
#     for technique in df[df["Log"]==log]["Extraction Technique"].unique():
#         plt.figure(figsize=figsize)
#         hue_order_local = hue_order.copy()
#         if log== "Order Management" or log == "Incident":
#             hue_order_local[0] = "Object Mapping - infeasible"
#         plot_df = df[(df["Log"]==log) & (df["Extraction Technique"]== technique)]
#         sns.lineplot(data = plot_df,x="Number of Process Executions",y="Computation Time", hue="Variant Computation", hue_order = hue_order_local)
#         if len(plot_df[(plot_df["Computation Time"] == 3000)]) != 0:
#             # Add a horizontal line for the timeout threshold
#             plt.axhline(y=3000, color='red', linestyle='--')
#
#             # Annotate the timeout line
#             plt.text(x=plot_df['Number of Process Executions'].min(), y=3000, s=' Computation Timeout', color='red',
#                      verticalalignment='bottom')
#             sns.scatterplot(data=plot_df[(plot_df["Computation Time"] == 3000)], x="Number of Process Executions", y="Computation Time",color = "red", marker = "X")
#         plt.ylabel('Computation Time (in s)')
#         plt.title('Variant Computation: '+log+' and '+technique, fontsize=15)
#         sns_settings(legend=True, legend_position = "upper left", size_reducer = 0)
#         plt.savefig("plots/algorithms/variant_scalability_"+log.replace(" ","_")+"_"+technique.replace(" ","_")+".pdf", format='pdf', transparent = False)
#         plt.show()
for log in df["Log"].unique():
    rows = (len(df[df["Log"]==log]["Extraction Technique"].unique())+1)//2
    print(rows)
    figsize = (7, 2.5 * rows+(4-rows)/2)
    fig, axes = plt.subplots(rows, 2, figsize=figsize)#, sharex=True, sharey=True)
    axes = axes.flatten()
    legend_handles = []
    legend_labels = []
    for idx, technique in enumerate(df[df["Log"]==log]["Extraction Technique"].unique()):
        ax = axes[idx]  # Select the subplot axis
        #plt.figure(figsize=figsize)
        hue_order_local = hue_order.copy()
        if log== "Order Management" or log == "Incident":
            hue_order_local[0] = "Object Mapping - infeasible"
        plot_df = df[(df["Log"]==log) & (df["Extraction Technique"]== technique)]
        sns.lineplot(data = plot_df,x="Number of Process Executions",y="Computation Time", hue="Variant Computation", hue_order = hue_order_local, ax = ax)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.get_legend().remove()
        if len(plot_df[(plot_df["Computation Time"] == 3000)]) != 0:
            # Add a horizontal line for the timeout threshold
            plt.axhline(y=3000, color='red', linestyle='--')

            # Annotate the timeout line
            plt.text(x=plot_df['Number of Process Executions'].min(), y=3000, s=' Computation Timeout', color='red',
                     verticalalignment='bottom')
            sns.scatterplot(data=plot_df[(plot_df["Computation Time"] == 3000)], x="Number of Process Executions", y="Computation Time",color = "red", marker = "X")
        ax.set_title(technique)
    #fig.ylabel('Computation Time (in s)')
    if log == "Loan Application" or log == "Incident":
        fig.delaxes(axes[-1])
    fig.text(0.5, 0.02, 'Number of Process Executions', ha='center', va='center',fontsize=16)
    fig.text(0.02, 0.5, 'Computation Time (in s)', ha='center', va='center', rotation='vertical',fontsize=16)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center')
    plt.tight_layout()
    plt.subplots_adjust(top=1-0.12*0.8*(4/rows)+(2-rows)*0.01)
    plt.subplots_adjust(bottom=0.07*0.8*(4/rows)-(2-rows)*0.01)
    plt.subplots_adjust(left=0.10)
    #sns_settings(legend=True, legend_position = "upper left", size_reducer = 0)
    plt.savefig("plots/algorithms/variant_scalability_"+log.replace(" ","_")+".pdf", format='pdf', transparent = False)
    plt.show()

example_df = df[(df["Log"]=="P2P" ) & (df["Extraction Technique"] =="Leading Type goods receipt") &(df["Variant Computation"] =="Object Mapping")]
sns.lineplot(data=example_df, x="Number of Process Executions", y="Computation Time", hue = "Variant Computation")
sns_settings()
plt.title("Variant Equivalence: P2P (Leading Type goods receipt)", fontsize =16)
plt.tight_layout()
plt.savefig("plots/variant_computation_naive_example.pdf")
plt.show()
