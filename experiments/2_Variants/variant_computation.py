from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE, NAIVE_MAPPING
import pandas as pd
from ocpa.algo.util.filtering.log import case_filtering
import numpy as np
import re
import os
from variant_computation_logic import compute_variants
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm


extraction_techniques = [CONN_COMP,LEAD_TYPE]
computation_techniques = [NAIVE_MAPPING,ONE_PHASE,TWO_PHASE]#[ONE_PHASE,TWO_PHASE]
json_logs = ["Order","P2P"]#["P2P"]#[]#["P2P"]#["P2P","Order"]
csv_logs = ["Incident","Fin"]#,"Incident"]#["Incident","Fin"]
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
    for i in range(10,11):
        filtered_ocel = case_filtering.filter_process_executions(ocel,cases = ocel.process_executions[0:int(len(ocel.process_executions)*(i/10))])
        ocel_export_factory.apply(filtered_ocel, "./sublogs/"+log+"_"+str(i)+".jsonocel")




################################ Experimental Part
results_list = []
total_param_space = []
for log in logs:
    param_space = []
    add_params = {}
    var_params = {}

    collected_add_params = []
    collected_var_params = []
    for extraction in extraction_techniques:
        # Connected components
        if extraction == CONN_COMP:
            add_params = {"execution_extraction": extraction}
            collected_add_params.append(add_params)
        # Leading Type
        elif extraction == LEAD_TYPE:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "leading_type": o_type}
                collected_add_params.append(add_params)
                #param_space.append(log_parameters[log] | add_params)
    for comp_type in computation_techniques:
        var_params = {"variant_calculation": comp_type, "timeout": 2000}
        if comp_type == ONE_PHASE:
            collected_var_params.append(var_params)
        #For Two Phase we need to specify the exact calculation
        if comp_type == TWO_PHASE:
            var_params = var_params | {"exact_variant_calculation": True}
            collected_var_params.append(var_params)
        # We cannot use naive in these cases as there are just too many objects and it does no terminate in a reasonable
        # time
        if log != "Incident" and log != "Order":
            if comp_type == NAIVE_MAPPING:
                collected_var_params.append(var_params)
                ####var_params = var_params | {"naive_project_object_set": True}
                ####collected_var_params.append(var_params)

    param_space = [{**d1, **d2} for d1 in collected_add_params for d2 in collected_var_params]
    param_space = [{**d1, **d2} for d1 in param_space for d2 in [{"Log Subsize":i}for i in range(1,11)]]
    param_space = [{**d1, **d2} for d1 in param_space for d2 in [{"Log": log}]]
    param_space = [{**d1, **d2} for d1 in param_space for d2 in [log_parameters[log]]]
    print(param_space)
    total_param_space += param_space

pool = ThreadPool(4)
results = list(tqdm(pool.imap(compute_variants, total_param_space), total=len(total_param_space)))
#results = compute_variants(total_param_space[0])
print(results)
results_dict = pd.DataFrame(results)
results_dict.to_csv("computationtime_results.csv")

#results_dict = pd.DataFrame(results)
#results_dict.to_csv("results_scalability_a_after_Fin_P2P_Order.csv")




