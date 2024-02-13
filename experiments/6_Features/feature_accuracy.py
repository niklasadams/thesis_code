from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE, SINGLE_FLATTENING
from ocpa.algo.predictive_monitoring import factory as predictive_monitoring
import pandas as pd
from ocpa.algo.predictive_monitoring import tabular
from sklearn.metrics import accuracy_score, mean_squared_error
from ocpa.algo.util.flattening import factory as flattening_factory


def evaluate_categorical_features(features, flat_features, cat_features):
    accuracy_results = {}
    #print(cat_features)
    #print(flat_features.columns)
    #print(features)
    #print(flat_features)
    # preprocess the feature tables such that event IDs are matching for each row
    #print(features[('event_char_value', ('event_id',))])
    # remove non intersecting events and ount the numbe rof removed events

    # Handle the convergence in flattening
    flat_event_ids = set(list(flat_features[('event_char_value', ('event_identifier',))].values))
    full_feature_length = len(features)
    print(len(features))
    features = features[features[('event_char_value', ('event_id',))].apply(lambda x: x in flat_event_ids)]
    print(len(features))
    feature_diff = len(features) - full_feature_length

    # sort according to event id
    features = features.sort_values(by = ('event_char_value', ('event_id',)))
    flat_features = flat_features.sort_values(by=('event_char_value', ('event_identifier',)))

    # for flat features we need to address the issue of convergence, i.e., an event being in the extracted
    # features multiple times with potentially different extracted values. For categorical features,
    # we employ a unanimous voting to agree on a feature value, i.e., the value will only be 1 if it
    # is 1 for every duplication of the event
    flat_features = flat_features.groupby(('event_char_value', ('event_identifier',))).agg("min").reset_index()

    # for each feature, determine the accuracy
    for feature in cat_features:
        feature_accuracy = accuracy_score(features[feature],flat_features[feature])
        accuracy_results[feature] = feature_accuracy
    return accuracy_results, feature_diff

def evaluate_numerical_metrics(features,flat_features, num_features):
    error_results = {}


    flat_event_ids = set(list(flat_features[('event_char_value', ('event_identifier',))].values))
    full_feature_length = len(features)
    features = features[features[('event_char_value', ('event_id',))].apply(lambda x: x in flat_event_ids)]
    feature_diff = len(features) - full_feature_length

    # sort according to event id
    features = features.sort_values(by=('event_char_value', ('event_id',)))
    flat_features = flat_features.sort_values(by=('event_char_value', ('event_identifier',)))

    # for flat features we need to address the issue of convergence, i.e., an event being in the extracted
    # features multiple times with potentially different extracted values. For numerical features,
    # we employ a mean voting to agree on a feature value
    flat_features = flat_features.groupby(('event_char_value', ('event_identifier',))).agg("mean").reset_index()

    for feature in num_features:
        # first, we normalize both feature value sets by their joined maximum to retrieve comparable metrics
        max_val = max(max(features[feature]),max(flat_features[feature] ))
        if max_val > 0.000001:
            features[feature] = features[feature] / max_val
            flat_features[feature] = flat_features[feature] / max_val
            error = mean_squared_error(features[feature],flat_features[feature])
        else:
            error = -1
        error_results[feature] = error
    return error_results, feature_diff


extraction_techniques = [CONN_COMP,SINGLE_FLATTENING]
connected_components_extraction = CONN_COMP
# Define Event Logs
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
                      {"starttime":"event_timestamp"},
                  "Fin":
                       {"obj_names": log_ots["Fin"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ",",
                        "starttime":"event_start_timestamp"},
                  "Order":
                        {"obj_names": log_ots["Order"],
                         "starttime":"event_timestamp"},
                  "Incident":
                        {"obj_names": log_ots["Incident"],
                         "val_names": [],
                         "act_name": "event_activity",
                         "time_name": "event_opened_at",
                         "sep": ",",
                         "starttime":"event_timestamp"
                         }
                  }


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
                   (predictive_monitoring.EVENT_SERVICE_TIME, (log_parameters[log]["starttime"],)),
                   (predictive_monitoring.EVENT_REMAINING_TIME, ()),
                   (predictive_monitoring.EVENT_ELAPSED_TIME, ()),
                   (predictive_monitoring.EVENT_FLOW_TIME, ()),
                   (predictive_monitoring.EVENT_SYNCHRONIZATION_TIME, ()),
                   (predictive_monitoring.EVENT_SOJOURN_TIME, ()),
                   (predictive_monitoring.EVENT_WAITING_TIME, (log_parameters[log]["starttime"],)),
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
    #print(features)


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
        print(param)

        # iteration: extract single type log for each type and composite flattened log
        flat_log = None
        if log in json_logs:
            flat_log = ocel_json_import_factory.apply(log_files[log], parameters=param)
        else:
            flat_log = ocel_csv_import_factory.apply(log_files[log], parameters=param)
        flat_log = flattening_factory.apply(flat_log)


        # extract relevant features
        feature_storage_flat = predictive_monitoring.apply(flat_log, feature_set+[(predictive_monitoring.EVENT_CHAR_VALUE, ("event_identifier",))], [], workers = 1)
        features_flat = tabular.construct_table(
            feature_storage_flat, index_list=list(range(0, len(feature_storage_flat.feature_graphs))))

        # compare accuracy of categorical features
        categorical_metrics, feature_diff = evaluate_categorical_features(features,features_flat, cat_feature_set) # (flat_features, features, cat_features)
        print(param["execution_extraction"])
        print(categorical_metrics)

        # compare MSE of numerical features
        numerical_metrics, diff = evaluate_numerical_metrics(features, features_flat, num_feature_set)
        print(numerical_metrics)

        #add results
        results.append(categorical_metrics | numerical_metrics | {"Log":log, "Flattening Difference": diff} | param)

result_df = pd.DataFrame(results)
result_df.to_csv("accuracy_results.csv", index = False)


