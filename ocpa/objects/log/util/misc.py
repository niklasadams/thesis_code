from ocpa.objects.log.variants.table import Table
from ocpa.objects.log.variants.graph import EventGraph
import ocpa.objects.log.converter.versions.df_to_ocel as obj_converter
import ocpa.objects.log.variants.util.table as table_utils


def remove_object_references(df, object_types, to_keep):
    for ot in object_types:
        df[ot] = df[ot].apply(lambda x: list(set(x) & to_keep[ot]))
    df = df[df[object_types].astype(bool).any(axis=1)]
    return df


def copy_log(ocel):
    from ocpa.objects.log.ocel import OCEL
    df = ocel.log.log
    log = Table(df, parameters=ocel.parameters)
    obj = obj_converter.apply(df)
    graph = EventGraph(table_utils.eog_from_log(log))
    new_log = OCEL(log, obj, graph, ocel.parameters)
    return new_log


def copy_log_from_df(df, parameters):
    from ocpa.objects.log.ocel import OCEL
    log = Table(df, parameters=parameters)
    obj = obj_converter.apply(df)
    graph = EventGraph(table_utils.eog_from_log(log))
    new_log = OCEL(log, obj, graph, parameters)
    return new_log


def get_objects_of_variants(ocel, variants):
    obs = {}
    for ot in ocel.object_types:
        obs[ot] = set()
    for v_id in variants:
        for case_id in ocel.variants_dict[ocel.variants[v_id]]:
            for ob in ocel.process_execution_objects[case_id]:
                obs[ob[0]].add(ob[1])

    return obs


def flatten_log(ocel, object_type):
    new_event_df = ocel.log.log.copy().explode(object_type,ignore_index = True)
    drop_object_types = [ot for ot in ocel.object_types if ot != object_type]
    new_event_df = new_event_df.drop(columns= drop_object_types)
    new_event_df = new_event_df[new_event_df[object_type].notnull()]
    new_event_df[object_type] = new_event_df[object_type].apply(lambda x: [x] if x else [])
    #new_event_df = new_event_df[new_event_df.apply(lambda x: len(x[object_type]) > 0 )]
    new_event_df["event_id"] = list(range(1,len(new_event_df)+1))
    params = ocel.parameters.copy()
    params["obj_names"] = [object_type]
    new_log = copy_log_from_df(new_event_df, params)
    return new_log