import pandas as pd
import time

def apply(ocel, parameters):
    '''
    Extracting process executions through fllatening on a single object type. Calling this method is usually
    integrated in the :class:`OCEL class <ocpa.objects.log.ocel.OCEL>` and is specified in the parameters usually set
    when importing the OCEL in :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    :param parameters: Dictionary containing type to be flattened to (usually already set when importing the event log)
    :type parameters: Dict
    :return: cases, object_mapping, case_mapping

    '''
    s_time = time.time()
    o_type = parameters["flattening_type"]
    log_df = ocel.log._log.copy()
    events_to_objects = pd.Series(log_df[o_type].values, index=log_df["event_id"]).to_dict()
    object_to_events = {}
    for event, objects in events_to_objects.items():
        for o in objects:
            object_to_events.setdefault(o, []).append(event)
    cases = []
    obs = []
    case_mapping = {}
    case_index = 0
    for o,case in object_to_events.items():
        obs.append([o])
        cases.append(case)
        for event in case:
            case_mapping.setdefault(event,[]).append(case_index)
        case_index+=1

    return cases, obs, case_mapping, time.time()-s_time