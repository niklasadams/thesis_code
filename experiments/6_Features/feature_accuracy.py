from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
import pandas as pd
from ocpa.algo.predictive_monitoring import tabular




extraction_techniques = [CONN_COMP,SINGLE_FLATTENING]
connected_components_extraction = CONN_COMP
# Define Event Logs
json_logs = ["P2P"]#,"Order"]
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

#TODO: ADD the starttime to the parameter set

results = []

# Iterate over event logs
for log in logs:

    # extract OC Log
    ocel = None
    if log in json_logs:
        ocel = ocel_json_import_factory.apply(log_files[log], parameters=log_parameters[log] | {"execution_extraction": connected_components_extraction})
    else:
        ocel = ocel_csv_import_factory.apply(log_files[log], parameters=log_parameters[log] | {"execution_extraction": connected_components_extraction})
    activities = list(set(ocel.log.log["event_activity"].tolist()))

    cat_feature_set = [

    ] +\
        [(predictive_monitoring.EVENT_ACTIVITY, (a,)) for a in activities] + \
        [(predictive_monitoring.EVENT_PRECEDING_ACTIVITES, (act,)) for act in activities] +\
        [(predictive_monitoring.EVENT_CURRENT_ACTIVITIES, (act,)) for act in activities]

    num_feature_set = [(predictive_monitoring.EVENT_CHAR_VALUE, ("event_id",)),
                   (predictive_monitoring.EVENT_NUM_OF_OBJECTS, ()),
                   (predictive_monitoring.EVENT_SERVICE_TIME, ("event_timestamp",)),
                   (predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ()),
                   (predictive_monitoring.EVENT_FLOW_TIME, ()),
                   (predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ()),
                   (predictive_monitoring.EVENT_SOJOURN_TIME, ()),
                   (predictive_monitoring.EVENT_WAITING_TIME, ("event_timestamp",)),
                   (predictive_monitoring.EVENT_PREVIOUS_OBJECT_COUNT,())] + \
                  [(predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, (t,)) for t in ocel.object_types] + \
                  [(predictive_monitoring.EVENT_TYPE_COUNT, (t,)) for t in ocel.object_types] + \
                  [(predictive_monitoring.EVENT_PREVIOUS_ACTIVITY_COUNT, (a,)) for a in activities] + \
                  [(predictive_monitoring.EVENT_PREVIOUS_TYPE_COUNT, (t,)) for t in ocel.object_types]  + \
                  [(predictive_monitoring.EVENT_POOLING_TIME, (t,)) for t in ocel.object_types]+ \
                  [(predictive_monitoring.EVENT_LAGGING_TIME, (t,)) for t in ocel.object_types]


    feature_set = [(predictive_monitoring.EVENT_CHAR_VALUE, ("event_id",))] + cat_feature_set +num_feature_set
    # extract relevant features
    feature_storage = predictive_monitoring.apply(ocel, feature_set, [], workers=1)
    features = tabular.construct_table(
        feature_storage, index_list=list(range(0,len(feature_storage.feature_graphs))))
    print(features)


    param_space = []
    for extraction in extraction_techniques:
        # Composite Type Flattening
        if extraction == CONN_COMP:
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


        # iteration: extract single type log for each type and composite flattened log
        for t in extraction_techniques:
            flat_log = None
            if log in json_logs:
                flat_log = ocel_json_import_factory.apply(log_files[log], parameters=param)
            else:
                flat_log = ocel_csv_import_factory.apply(log_files[log], parameters=param)
            # extract relevant features
            feature_storage_flat = predictive_monitoring.apply(ocel, feature_set, [])
            features_flat = tabular.construct_table(
                feature_storage_flat, index_list=list(range(0, len(feature_storage_flat.feature_graphs))))
            print(features_flat)
            # compare accuracy of categorical features
            categorical_metrics = None # (flat_features, features, cat_features)
            # compare MSE of numerical features
            numerical_metrics = None # (flat_features, features, num_features)

            #add results
            results.append(None)

result_df = pd.DataFrame(results)
#result_df.to_csv("accurace_results.csv", index = False)


