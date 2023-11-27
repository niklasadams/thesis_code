from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING
import pandas as pd


extraction_techniques = [CONN_COMP,LEAD_TYPE,SINGLE_FLATTENING]
json_logs = ["P2P","Order"]
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

results_list = []

for log in logs:
    param_space = []
    for extraction in extraction_techniques:
        # Connected components
        if extraction == CONN_COMP:
            add_params = {"execution_extraction":extraction}
            param_space.append(log_parameters[log]|add_params)
            #Post flattening connected components
            add_params = {"execution_extraction": extraction, "Post-extraction flattening":True}
            param_space.append(log_parameters[log] | add_params)
        # Leading Type
        elif extraction == LEAD_TYPE:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "leading_type":o_type}
                param_space.append(log_parameters[log] | add_params)
        elif extraction == SINGLE_FLATTENING:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "flattening_type":o_type}
                param_space.append(log_parameters[log] | add_params)
    for param in param_space:
        print(param)

        if "Post-extraction flattening" not in param:
            param["Post-extraction flattening"] = False
        if log in json_logs:
            ocel = ocel_json_import_factory.apply(log_files[log], parameters = param)
        else:
            ocel = ocel_csv_import_factory.apply(log_files[log], parameters = param)

        results = extraction_metric_factory.apply(ocel, parameters = param)
        print(results)
        o_type = None
        if "flattening_type" in param.keys():
            o_type = param["flattening_type"]
        elif "leading_type" in param.keys():
            o_type = param["leading_type"]

        extraction_technique = param["execution_extraction"]
        if param["Post-extraction flattening"]:
            extraction_technique += " Flattened"
        results_list.append({
            "Log":log,
            "Extraction Technique":extraction_technique,
            "Type": o_type
        } | results
        )
        #Descriptive statistics
        print(param)
        print("Number of Events"+str(len(ocel.log.log)))
        print("Number of Types" + str(len(ocel.object_types)))
        all_objects = set()
        min_o_count, max_o_count = 10000000,0
        sum_o_counts = 0
        min_e_count, max_e_count = 10000000, 0
        sum_e_counts = 0
        for i in range(0,len(ocel.process_executions)):
            p_obs = ocel.process_execution_objects[i]
            p_evs = ocel.process_executions[i]
            num_evs = len(p_evs)
            if num_evs > max_e_count:
                max_e_count = num_evs
            if min_e_count > num_evs:
                min_e_count = num_evs
            sum_e_counts += num_evs


            all_objects = all_objects.union(set(p_obs))
            num_obs = len(p_obs)
            if num_obs > max_o_count:
                max_o_count = num_obs
            if min_o_count > num_obs:
                min_o_count = num_obs
            sum_o_counts += num_obs
        print("Number of Objects" + str(len(all_objects)))
        print("Number of Process Executions" + str(len(ocel.process_executions)))
        print("Min Events per Execution" + str(min_e_count))
        print("Max Events per Execution" + str(max_e_count))
        print("Avg Events per Execution" + str(sum_e_counts / len(ocel.process_executions)))
        print("Min Objects per Execution" + str(min_o_count))
        print("Max Objects per Execution" + str(max_o_count))
        print("Avg Objects per Execution" + str(sum_o_counts/len(ocel.process_executions)))
    results_df = pd.DataFrame(results_list)
    results_df.to_csv("results_after_"+log+".csv")
results_df = pd.DataFrame(results_list)
results_df.to_csv("results.csv")





