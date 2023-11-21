import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING

def sns_settings():
    ax = plt.gca()
    plt.legend(loc='lower right',fontsize=10)
    ax.set_xlabel(ax.get_xlabel(), fontsize=16)
    ax.set_ylabel(ax.get_ylabel(), fontsize=16)
    plt.xticks(rotation=0,fontsize = 14)
    plt.yticks(rotation=0, fontsize=14)
    plt.tight_layout()

sns.color_palette("tab10")
sns.set_theme()
df = pd.read_csv("runtime_results.csv")
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
mask = df["Extraction Technique"] == "Composite-Type Flattening"
df["Type"][mask] = 1
mask = df["Extraction Technique"] == "Connected Components"
df["Type"][mask] = 2
figsize = (7,5)


plt.figure(figsize=figsize)
sns.lineplot(df,x="Number of Events",y="Extraction Time", hue = "Log", style = "Extraction Technique",units = "Type", estimator = None,linewidth = 2, markers= True)
plt.xscale('log')
plt.yscale('log')
sns_settings()
plt.savefig("runtime.png",dpi=400)
plt.show()