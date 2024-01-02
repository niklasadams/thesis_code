import math

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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

df = pd.read_csv("results_variants_b_cluster_p2p.csv")
df2 = pd.read_csv("results_variants_b_cluster_order.csv")
df = df.append(df2, ignore_index=True)
df2 = pd.read_csv("results_variants_b_cluster_inc.csv")
df = df.append(df2, ignore_index=True)
df2 = pd.read_csv("results_variants_b_cluster_fin.csv")
df = df.append(df2, ignore_index=True)
print(df.columns)
print(df.head())
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
df["Hashing Function"] = df["Hashing Function"].replace({"weisfeiler-lehman-1-iteration":"WL 1 Iteration",
             "weisfeiler-lehman-2-iterations":"WL 2 Iterations",
             "weisfeiler-lehman-standard-3-iterations":"WL 3 Iterations"})
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Extraction Technique"] = df.apply(lambda x: x["Extraction Technique"] +" "+x["Type"] if isinstance(x["Type"],str) else x["Extraction Technique"],axis =1)
# for log in df["Log"].unique():
#     print(log)
#     for technique in df[df["Log"]==log]["Extraction Technique"].unique():
#         plt.figure(figsize=figsize)
#         plot_df = df[(df["Log"] == log) & (df["Extraction Technique"] == technique)]
#         ax = sns.lineplot(plot_df,x="Number of Process Executions",y="Computation Time", hue = "Hashing Function")
#         ax.set_title("Variant Computation: Different Hashing Function for " + log + " and " + technique)
#         ax.set_xlabel("Number of Process Executions")
#         ax.set_ylabel("Total Variant Computation Time (in s)")
#         plt.savefig("plots/hashing/comparison/"+log.replace(" ","_")+"_"+technique.replace(" ","_")+".pdf")
#         plt.show()
#
#
#
#         pivoted_df = plot_df.pivot(index='Number of Process Executions', columns='Hashing Function',
#                                    values=['Hashing Time', 'Validation Time'])
#         fig, ax = plt.subplots(figsize=figsize)
#         hashing_functions = plot_df['Hashing Function'].unique()
#         num_executions = plot_df['Number of Process Executions'].unique()
#         group_width = 0.8
#         bar_width = group_width / len(hashing_functions)
#         for i, function in enumerate(hashing_functions):
#             x = np.arange(len(num_executions)) - (group_width - bar_width) / 2 + i * bar_width
#             ax.bar(x, pivoted_df[('Hashing Time', function)], width=bar_width, label=f'{function} - Hashing Time')
#             ax.bar(x, pivoted_df[('Validation Time', function)], width=bar_width, label=f'{function} - Validation Time',
#                    bottom=pivoted_df[('Hashing Time', function)])
#         ax.set_xlabel("Number of Process Executions")
#         ax.set_ylabel("Computation Time (in s)")
#         ax.set_xticks(np.arange(len(num_executions)))
#         ax.set_xticklabels(num_executions)
#         ax.legend(title="Hashing Function and Time Type")
#         ax.set_title("Decomposition into Hashing and Validation Times for "+log+" and "+technique)
#         plt.savefig("plots/hashing/decomposed/" + log.replace(" ", "_") + "_" + technique.replace(" ", "_") + ".pdf")
#         plt.show()


for log in df["Log"].unique():
    rows = (len(df[df["Log"]==log]["Extraction Technique"].unique())+1)//2
    print(rows)
    figsize = (7, 2.5 * rows+(4-rows)/2)
    fig, axes = plt.subplots(rows, 2, figsize=figsize)#, sharex=True, sharey=True)
    axes = axes.flatten()

    for idx, technique in enumerate(df[df["Log"]==log]["Extraction Technique"].unique()):
        ax = axes[idx]  # Select the subplot axis
        #plt.figure(figsize=figsize)

        plot_df = df[(df["Log"] == log) & (df["Extraction Technique"] == technique)]
        ax = sns.lineplot(plot_df, x="Number of Process Executions", y="Computation Time", hue="Hashing Function", ax = ax)
        #ax.set_title("Variant Computation: Different Hashing Function for " + log + " and " + technique)
        #ax.set_xlabel("Number of Process Executions")
        #ax.set_ylabel("Total Variant Computation Time (in s)")
        #plt.savefig("plots/hashing/comparison/" + log.replace(" ", "_") + "_" + technique.replace(" ", "_") + ".pdf")
        #plt.show()


        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.get_legend().remove()
        ax.set_title(technique)

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
    plt.savefig("plots/hashing/comparison/"+log.replace(" ","_")+".pdf", format='pdf', transparent = False)
    plt.show()

for log in df["Log"].unique():
    rows = (len(df[df["Log"]==log]["Extraction Technique"].unique())+1)//2
    print(rows)
    figsize = (7, 2.7 * rows+(4-rows)/2)
    fig, axes = plt.subplots(rows, 2, figsize=figsize)#, sharex=True, sharey=True)
    axes = axes.flatten()

    for idx, technique in enumerate(df[df["Log"]==log]["Extraction Technique"].unique()):
        ax = axes[idx]  # Select the subplot axis
        #plt.figure(figsize=figsize)
        plot_df = df[(df["Log"] == log) & (df["Extraction Technique"] == technique)]
        pivoted_df = plot_df.pivot(index='Number of Process Executions', columns='Hashing Function',
                                  values=['Hashing Time', 'Validation Time'])
        hashing_functions = plot_df['Hashing Function'].unique()
        num_executions = plot_df['Number of Process Executions'].unique()
        group_width = 0.8
        bar_width = group_width / len(hashing_functions)
        for i, function in enumerate(hashing_functions):
            x = np.arange(len(num_executions)) - (group_width - bar_width) / 2 + i * bar_width
            ax.bar(x, pivoted_df[('Hashing Time', function)], width=bar_width, label=f'{function} - Hashing Time')
            ax.bar(x, pivoted_df[('Validation Time', function)], width=bar_width, label=f'{function} - Validation Time',
                   bottom=pivoted_df[('Hashing Time', function)])
        #ax.set_xlabel("Number of Process Executions")
        #ax.set_ylabel("Computation Time (in s)")
        ax.set_xticks(np.arange(len(num_executions)),labelsize=6)
        ax.set_xticklabels(num_executions,rotation = -45)
        ax.legend(title="Hashing Function and Time Type")


        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.get_legend().remove()
        ax.set_title(technique)

    if log == "Loan Application" or log == "Incident":
        fig.delaxes(axes[-1])
    fig.text(0.5, 0.02, 'Number of Process Executions', ha='center', va='center',fontsize=16)
    fig.text(0.02, 0.5, 'Computation Time (in s)', ha='center', va='center', rotation='vertical',fontsize=16)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center',fontsize=10,ncol=2)
    plt.tight_layout()
    plt.subplots_adjust(top=1-0.12*0.8*(4/rows)+(2-rows)*0.01)
    plt.subplots_adjust(bottom=0.07*0.8*(4/rows)-(2-rows)*0.01)
    plt.subplots_adjust(left=0.10)
    #sns_settings(legend=True, legend_position = "upper left", size_reducer = 0)
    plt.savefig("plots/hashing/decomposed/"+log.replace(" ","_")+".pdf", format='pdf', transparent = False)
    plt.show()