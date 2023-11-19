from ocpa.objects.log.ocel import OCEL
from typing import Dict


def apply(ocel: OCEL, parameters=None) -> Dict[str,float]:
    #Post extraction flattening is flattening to emulate the extraction of sequence from connected objects on the event
    #log extraction level. Since ocpa always infers the precendece constraints from the event log, we need to use another way
    #to compute the precedecne constraints after flattening
    post_extraction_flattening = parameters["Post-extraction flattening"]
    print(len(ocel.process_executions))
    return {"convergence_freeness":convergence_freeness(ocel),
            "deficiency_freeness":deficiency_freeness(ocel),
            "divergence_freeness":divergence_freeness(ocel, post_extraction_flattening = post_extraction_flattening)}


def convergence_freeness(ocel):
    p_events_unique = set()
    p_events = []
    for p_exec in ocel.process_executions:
        p_events_unique = p_events_unique.union(p_exec)
        p_events += p_exec
    return len(p_events_unique)/len(p_events)

def deficiency_freeness(ocel):
    p_events = set()
    for p_exec in ocel.process_executions:
        p_events = p_events.union(p_exec)
    return len(p_events)/len(set(ocel.log.log["event_id"].unique()))

def divergence_freeness(ocel, post_extraction_flattening=False):
    p_edges = set()
    for i in range(0,len(ocel.process_executions)):
        if not post_extraction_flattening:
            p_edges = p_edges.union(ocel.get_process_execution_graph(i).edges)
        else:
            p_edges = p_edges.union(ocel.get_flattened_process_execution_graph(i).edges)
    log_edges = set(ocel.graph.eog.edges)
    edges_in_p_from_log = len(log_edges.intersection(p_edges))
    div_freeness = (edges_in_p_from_log/len(log_edges)) * (edges_in_p_from_log/len(p_edges))
    return div_freeness