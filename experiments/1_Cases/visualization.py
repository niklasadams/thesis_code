import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING

def sns_settings():
    ax = plt.gca()
    plt.legend(loc='lower left',fontsize=14)
    ax.set_xlabel(ax.get_xlabel(), fontsize=16)
    ax.set_ylabel(ax.get_ylabel(), fontsize=16)
    plt.xticks(rotation=-9,fontsize = 14)
    plt.yticks(rotation=0, fontsize=14)
    plt.tight_layout()

sns.color_palette("tab10")
sns.set_theme()
CONV = "Convergence Freeness"
DEFI = "Deficiency Freeness"
DIVE = "Divergence Freeness"
df = pd.read_csv("results.csv")
df = df.rename(columns = {"convergence_freeness":CONV,"deficiency_freeness":DEFI,"divergence_freeness":DIVE})
df["Extraction Technique"] = df["Extraction Technique"].replace({CONN_COMP:"Connected Components",LEAD_TYPE:"Leading Type",SINGLE_FLATTENING:"Single-Type Flattening",CONN_COMP +" Flattened":"Composite-Type Flattening"})
df["Log"] = df["Log"].replace({"P2P":"P2P",
             "Fin":"Loan Application",
             "Order":"Order Management",
             "Incident":"Incident"})
figsize = (9,5)

plt.figure(figsize=figsize)
sns.barplot(data = df,hue="Log",y=CONV,x="Extraction Technique")
sns_settings()
plt.savefig("convergence.png",dpi=400)
plt.show()

plt.figure(figsize=figsize)
sns.barplot(data = df,hue="Log",y=DEFI,x="Extraction Technique")
sns_settings()
plt.savefig("deficiency.png",dpi=400)
plt.show()

plt.figure(figsize=figsize)
sns.barplot(data = df,hue="Log",y=DIVE,x="Extraction Technique")
sns_settings()
plt.savefig("divergence.png",dpi=400)
plt.show()



df_exploded = pd.melt(df, id_vars=["Log","Extraction Technique","Type"], value_vars=[CONV,DEFI,DIVE])
df_exploded = df_exploded.rename(columns= {"variable":"Metric","value":"Value"})

plt.figure(figsize=figsize)
sns.barplot(data = df_exploded, hue="Metric", y="Value", x="Extraction Technique")
sns_settings()
plt.savefig("summarization.png",dpi=400)
plt.show()
