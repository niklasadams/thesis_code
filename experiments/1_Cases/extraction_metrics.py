from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE

extraction_techniques = [CONN_COMP,LEAD_TYPE]
json_logs = ["P2P","Order"]
csv_logs = ["Fin"]
logs = json_logs + csv_logs
log_files = {"P2P":"../../sample_logs/jsonocel/p2p-normal.jsonocel",
             "Fin":"../../sample_logs/csv/BPI2017-Final.csv",
             "Order":"../../sample_logs/jsonocel/order_management.jsonocel"}
log_ots = {"P2P": ['PURCHORD', 'INVOICE', 'PURCHREQ', 'MATERIAL', 'GDSRCPT'],
           "Fin":["application", "offer"],
           "Order":["items","orders","packages"]}
log_parameters = {"P2P":
                      {},
                  "Fin":
                       {"obj_names": log_ots["Order"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ","},
                  "Order":
                        {"obj_names": log_ots["Order"]}
                  }



for log in logs:
    param_space = []
    for extraction in extraction_techniques:
        # Connected components
        if extraction == CONN_COMP:
            add_params = {"execution_extraction":extraction}
            param_space.append(log_parameters[log]|add_params)
        # Leading Type
        elif extraction == LEAD_TYPE:
            for o_type in log_ots[log]:
                add_params = {"execution_extraction": extraction, "leading_type":o_type}
                param_space.append(log_parameters[log] | add_params)
    for param in param_space:
        if log in json_logs:
            ocel = ocel_json_import_factory.apply(log_files[log], parameters = param)
        else:
            ocel = ocel_csv_import_factory.apply(log_files[log], parameters = param)
        results = extraction_metric_factory.apply(ocel)
        print(results)




