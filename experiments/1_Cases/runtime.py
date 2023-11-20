from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING
import pandas as pd
from ocpa.algo.util.filtering.log import time_filtering
import numpy as np
import re
import os


extraction_techniques = [CONN_COMP,LEAD_TYPE,SINGLE_FLATTENING]
json_logs = []#["P2P","Order"]
csv_logs = ["Incident","Fin"]
logs = json_logs + csv_logs
log_files = {"P2P":"../../sample_logs/jsonocel/P2P_large.jsonocel",
             "Fin":"../../sample_logs/csv/BPI2017-Final.csv",
             "Order":"../../sample_logs/jsonocel/order_management.jsonocel",
             "Incident":"../../sample_logs/csv/incident_preprocessed.csv"}
log_ots = {"P2P": ['purchase_order', 'quotation', 'material', 'goods receipt', 'payment', 'purchase_requisition', 'invoice receipt'],#['PURCHORD', 'INVOICE', 'PURCHREQ', 'MATERIAL', 'GDSRCPT'],
           "Fin":["application", "offer"],
           "Order":["items","orders","packages"],
           "Incident":["incident","customer"]}
log_parameters = {"P2P":
                      {},
                  "Fin":
                       {"obj_names": log_ots["Fin"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ","},
                  "Order":
                        {"obj_names": log_ots["Order"]},
                  "Incident":
                        {"obj_names": log_ots["Incident"],
                         "val_names": [],
                         "act_name": "event_activity",
                         "time_name": "event_opened_at",
                         "sep": ","
                         }
                  }
#construct subsample logs, comment out if done once
for log in logs:

    # skipping mechanism in case the sublogs are already extracted
    pattern = re.compile(log+"_\d+.jsonocel")
    dir = "./sublogs/"
    sublogs_already_extracted = False
    for filepath in os.listdir(dir):
        if pattern.match(filepath):
            sublogs_already_extracted = True
            break
    if sublogs_already_extracted:
        continue
    #### skipping mechanism over


    if log in json_logs:
        ocel = ocel_json_import_factory.apply(log_files[log], parameters=log_parameters[log])
    else:
        ocel = ocel_csv_import_factory.apply(log_files[log], parameters=log_parameters[log])
    for i in range(1,11):
        perc = i/10
        end_timestamp = max(ocel.log.log['event_timestamp'])
        start_timestamp = min(ocel.log.log['event_timestamp'])
        filter_date = None
        if log == "P2P":
            filter_date = pd.Timestamp((start_timestamp.asm8.astype(np.int64) + perc*(end_timestamp.asm8.astype(np.int64) - start_timestamp.asm8.astype(np.int64))).astype('<M8[ns]'),tz= 'Europe/Brussels')
        else:
            filter_date = pd.Timestamp((start_timestamp.asm8.astype(np.int64) + perc * (
                        end_timestamp.asm8.astype(np.int64) - start_timestamp.asm8.astype(np.int64))).astype('<M8[ns]'))
        filtered_ocel = time_filtering.events(ocel,start=start_timestamp,end=filter_date)
        ocel_export_factory.apply(filtered_ocel, "./sublogs/"+log+"_"+str(i)+".jsonocel")



################################ Experimental Part
results_list = []

for log in logs:
    param_space = []
    for extraction in extraction_techniques:
        # Connected components
        if extraction == CONN_COMP:
            add_params = {"execution_extraction": extraction}
            param_space.append(log_parameters[log] | add_params)
            # Post flattening connected components
            add_params = {"execution_extraction": extraction, "Post-extraction flattening": True}
            param_space.append(log_parameters[log] | add_params)
        # Leading Type
        elif extraction == LEAD_TYPE:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "leading_type": o_type}
                param_space.append(log_parameters[log] | add_params)
        elif extraction == SINGLE_FLATTENING:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "flattening_type": o_type}
                param_space.append(log_parameters[log] | add_params)
    for param in param_space:
        if "Post-extraction flattening" not in param:
            param["Post-extraction flattening"] = False
        for i in range(1, 11):
            print(i)
            ocel = ocel_json_import_factory.apply("./sublogs/"+log+"_"+str(i)+".jsonocel", parameters=param)
            extraction_time = ocel.extraction_time
            o_type = None
            if "flattening_type" in param.keys():
                o_type = param["flattening_type"]
            elif "leading_type" in param.keys():
                o_type = param["leading_type"]
            results_list.append({
                "Log":log,
                "Number of Events":len(ocel.log.log),
                "Extraction Technique":param["execution_extraction"],
                "Type": o_type,
                "Extraction Time":extraction_time
            })
    results_dict = pd.DataFrame(results_list)
    results_dict.to_csv("runtime_results_after_"+log+".csv")

results_dict = pd.DataFrame(results_list)
results_dict.to_csv("runtime_results.csv")