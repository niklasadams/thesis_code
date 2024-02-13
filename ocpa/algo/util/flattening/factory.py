import ocpa.algo.util.process_executions.factory
from ocpa.objects.log.util import misc as log_util


def apply(ocel):
    '''
    Constructs a new ocel objects with only the objects assigned by the process executions to retrieve a clean new flattened event log.
    Parameters
    ----------
    ocel

    Returns
    -------

    '''
    log_copy = ocel.log.log.copy()

    # get process executions
    #process_executions, process_execution_objects, process_execution_mappings, extraction_time = VERSIONS[variant](ocel, parameters=parameters)

    # store the original event identifier
    log_copy["event_identifier"] = log_copy["event_id"]

    # get the cases for each event
    log_copy["case_object"] = log_copy["event_id"].apply(lambda x: [str(ob) for ob in ocel.process_execution_mappings[x]] if x in ocel.process_execution_mappings.keys() else [])

    # remove events without case, i.e., object
    log_copy["to_keep"] = log_copy["case_object"].apply(lambda x: False if len(x) == 0 else True)
    log_copy = log_copy[log_copy["to_keep"]]
    log_copy = log_copy.drop(columns = ["to_keep"])

    # explode the event df to duplicate events with multiple cases
    log_copy = log_copy.explode("case_object")
    log_copy["case_object"] = log_copy["case_object"].apply(lambda x: [x])

    # drop old object columns
    # We do not need to drop these columns because we set the object types and the other columns will be treated as
    # as attributes
    # log_copy = log_copy.drop(columns = ocel.object_types)

    # change parameter set
    new_params = ocel.parameters
    new_params["obj_names"] = ["case_object"]
    new_params["execution_extraction"] = ocpa.algo.util.process_executions.factory.CONN_COMP



    # transform to a new ocel object
    new_log = log_util.copy_log_from_df(log_copy, new_params)

    return new_log
