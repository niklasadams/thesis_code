from collections import Counter


def project_subgraph_on_activity(ocel, v_g, case_id, mapping_objects, mapping_activity):
    v_g_ = v_g.copy()
    for node in v_g.nodes():
        if not set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id]):
            v_g_.remove_node(node)
            continue
        node_object_types = [e[0] for e in sorted(list(set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id])))]
        #node_object_type_frequency = Counter(node_object_types)
        v_g_.nodes[node]['label'] = mapping_activity[node] + ": ".join(#":".join([f"{element}{freq}" for element, freq in node_object_type_frequency.items()])#mapping_activity[node] + ": ".join(
            [e[0] for e in node_object_types])
    for edge in v_g.edges():
        source, target = edge
        if not set(mapping_objects[source]) & set(mapping_objects[target]) & set(ocel.process_execution_objects[case_id]):
            v_g_.remove_edge(source, target)
            continue
        edge_object_types = sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(
                ocel.process_execution_objects[case_id])))
        #edge_object_type_frequency = Counter(edge_object_types)
        v_g_.edges[edge]['type'] = ": ".join(#":".join([f"{element}{freq}" for element, freq in edge_object_type_frequency.items()])#": ".join(
            [e[0] for e in edge_object_types])
        #v_g_.edges[edge]['label'] = ": ".join(
        #    [str(e) for e in sorted(list(set(mapping_objects[source]).intersection(set(mapping_objects[target])) & set(
        #        ocel.process_execution_objects[case_id])))])
    return v_g_

def project_subgraph_on_activity_and_objects(ocel, v_g, case_id, mapping_objects, mapping_activity):
    v_g_ = v_g.copy()
    for node in v_g.nodes():
        if not set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id]):
            v_g_.remove_node(node)
            continue
        v_g_.nodes[node]['label'] = mapping_activity[node]
        v_g_.nodes[node]['objects'] = set([e for e in sorted(list(set(mapping_objects[node]) & set(ocel.process_execution_objects[case_id])))])
    return v_g_

