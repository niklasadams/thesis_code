from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE
import pandas as pd
from ocpa.algo.util.filtering.log import case_filtering
import numpy as np
import re
import os


extraction_techniques = [CONN_COMP,LEAD_TYPE]
computation_techniques = [ONE_PHASE,TWO_PHASE]
json_logs = ["P2P"]#["P2P","Order"]
csv_logs = []#["Incident","Fin"]
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

    #change to by process execution filtering
    if log in json_logs:
        ocel = ocel_json_import_factory.apply(log_files[log], parameters=log_parameters[log])
    else:
        ocel = ocel_csv_import_factory.apply(log_files[log], parameters=log_parameters[log])
    for i in range(1,11):
        filtered_ocel = case_filtering.filter_process_executions(ocel,cases = ocel.process_executions[0:int(len(ocel.process_executions)*(i/10))])
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
        # Leading Type
        elif extraction == LEAD_TYPE:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "leading_type": o_type}
                param_space.append(log_parameters[log] | add_params)
    for param in param_space:
        if "Post-extraction flattening" not in param:
            param["Post-extraction flattening"] = False
        for i in range(1, 11):
            print(i)
            for comp_type in computation_techniques:
                par = param | {"variant_calculation":comp_type, "timeout":100}
                ocel = ocel_json_import_factory.apply("./sublogs/"+log+"_"+str(i)+".jsonocel", parameters=par)
                computation_time = ocel.variant_computation_time
                o_type = None
                if "leading_type" in param.keys():
                    o_type = param["leading_type"]
                extraction_technique = param["execution_extraction"]
                results_list.append({
                    "Log":log,
                    "Number of Events":len(ocel.log.log),
                    "Extraction Technique":extraction_technique,
                    "Variant Computation":comp_type,
                    "Type": o_type,
                    "Computation Time":computation_time
                })
    results_dict = pd.DataFrame(results_list)
    results_dict.to_csv("computationtime_results_after_"+log+".csv")

results_dict = pd.DataFrame(results_list)
results_dict.to_csv("computationtime_results.csv")