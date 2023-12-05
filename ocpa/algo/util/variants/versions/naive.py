import itertools
import time
import networkx as nx
import ocpa.algo.util.variants.versions.utils.helper as helper_functions
from tqdm import tqdm

def _isomorphism_under_object_mapping(p1,p2,object_mapping):
    def node_equivalence_under_object_mapping(n1, n2):
        mapped_node_objects = {object_mapping[o[0]][o] for o in n1['objects']}
        return n1['label'] == n2['label'] and mapped_node_objects == n2['objects']

    return nx.is_isomorphic(p1, p2, node_match=node_equivalence_under_object_mapping)

def _isomorphism_under_object_mapping_vf2pp(p1,p2,object_mapping):
    def project_labels(p, object_mapping= None):

        for n1 in p.nodes():
            node_obs = None
            if object_mapping:
                node_obs = {object_mapping[o[0]][o] for o in p.nodes[n1]['objects']}
            else:
                node_obs = p.nodes[n1]['objects']
            p.nodes[n1]['label'] = p.nodes[n1]['label'] + ",".join([ob_t+","+ob for ob_t, ob in sorted(list(node_obs))])
        return p

    return nx.vf2pp_is_isomorphic(project_labels(p1,object_mapping), project_labels(p2,object_mapping=None), node_label = 'label')

def _to_type_sep_set(objects_set):
    types = set([o[0] for o in objects_set])
    sep_objects = {}
    for t in types:
        sep_objects[t] = set()
        for o in objects_set:
            if t == o[0]:
                sep_objects[t].add(o)
    return sep_objects

def _map_object_mapping(p1_obs, p2_obs):
    mapping_dict = {}
    for t in p1_obs.keys():
        mapping_dict[t] = dict(zip(p1_obs[t], p2_obs[t]))
    return mapping_dict


def _generate_all_type_permutations(sep_objects):
    perms = {}
    for t in sep_objects:
        perms[t]= itertools.permutations(sep_objects[t])
    return perms

def apply(ocel, parameters):
    '''
    Determining variants in the most naive approach by performing a one-to-one isomorphism comparison of the graph with labels and additionally chekcing for the existence of an object mapping.
    between process executions. Calling this method is usually integrated in the :class:`OCEL class <ocpa.objects.log.ocel.OCEL>` and
    is specified in the parameters usually set when importing the OCEL in
    :func:`CSV importer <ocpa.objects.log.importer.csv.factory.apply>`
    or :func:`JSONOCEL importer <ocpa.objects.log.importer.ocel.factory.apply>`
    or :func:`JSONXML importer <ocpa.objects.log.importer.ocel.factory.apply>`.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`
    :param parameters: Parameters for the method. Keys contain:
        - "timeout" in s for aborting variant calculation
    :type parameters: : Dict
    :return: variants, v_freq_list, variant_graphs, variants_dict

    '''
    s_time = time.time()
    timeout = parameters["timeout"] if "timeout" in parameters.keys() else 3600
    project_object_set = parameters["naive_project_object_set"] if "naive_project_object_set" in parameters.keys() else False
    ocel.log.log["event_objects"] = ocel.log.log.apply(lambda x: [(ot, o) for ot in ocel.object_types for o in x[ot]],
                                               axis=1)
    variants_dict = dict()
    variants_graph_dict = dict()
    variant_graphs = dict()
    case_id = 0
    mapping_activity = dict(
        zip(ocel.log.log["event_id"], ocel.log.log["event_activity"]))
    mapping_objects = dict(
        zip(ocel.log.log["event_id"], ocel.log.log["event_objects"]))
    for v_g in ocel.process_executions:
        case = helper_functions.project_subgraph_on_activity_and_objects(ocel, ocel.graph.eog.subgraph(
            v_g), case_id, mapping_objects, mapping_activity)
        variant = "ArbitraryVariantString"
        variant_string = variant
        if variant_string not in variants_dict:
            variants_dict[variant_string] = []
            variants_graph_dict[variant_string] = []
            variant_graphs[variant_string] = (
                case, ocel.process_execution_objects[case_id])  # EOG.subgraph(v_g)#case
        variants_dict[variant_string].append(case_id)
        variants_graph_dict[variant_string].append(case)
        case_id += 1
    start_time = time.time()
    # refine the classes
    for _class in variants_graph_dict.keys():
        subclass_counter = 0
        subclass_mappings = {}
        for j in range(0, len(variants_graph_dict[_class])):
            exec = variants_graph_dict[_class][j]
            case_id = variants_dict[_class][j]
            exec_objects = ocel.process_execution_objects[case_id]
            found = False
            #print("Exec  "+str(j))
            for i in range(1, subclass_counter + 1):
                #print("Test to "+str(i))
                if nx.faster_could_be_isomorphic(exec, subclass_mappings[i][0][0]):
                    # First, check if object number matches to speed up computation
                    if len(ocel.process_execution_objects[case_id]) == len(ocel.process_execution_objects[subclass_mappings[i][0][1]]):

                        # Check potential matchings
                        # Map objects of the same type onto each other
                        # A mapping is a set of mappings per object type
                        p1_sep_objects = _to_type_sep_set(exec_objects)
                        p2_sep_objects = _to_type_sep_set(ocel.process_execution_objects[subclass_mappings[i][0][1]])

                        #We can check the individual type counts to already abort checking if there is no match in numbers
                        if set(p1_sep_objects.keys()) != set(p2_sep_objects.keys()):
                            continue
                        early_abort = False
                        for t in p1_sep_objects.keys():
                            if len(p1_sep_objects[t]) != len(p2_sep_objects[t]):
                                early_abort = True
                        if early_abort:
                            continue

                        # We generate all permutations of objects of each type and build the cartesian to generate
                        # all possible mappings
                        p2_type_permutations = _generate_all_type_permutations(p2_sep_objects)
                        product = itertools.product(*p2_type_permutations.values())
                        sep_object_permutations = [dict(zip(p2_type_permutations.keys(), combination)) for combination in product]

                        # We check each mapping for isomoprhism. The function to check isomorphism checks nodes
                        # for label equivalence and object set equivalence
                        for object_mapping_permutation in sep_object_permutations:#object_permutations:
                            object_mapping = _map_object_mapping(p1_sep_objects,object_mapping_permutation)#dict(zip(exec_objects, object_mapping_permutation))
                            is_isomorphic = False

                            #Check isomorphism, there are two different possibilities:
                            # 1. we can check and directly checkwhether the mapped object sets are equal. We need to define a custom matching
                            # function and use vf2
                            # We can lexicographically sort the object identifiers and marge them into a string together with the
                            # activity label. We can then use vf2pp as we are only comparing labels

                            if project_object_set:
                                is_isomorphic = _isomorphism_under_object_mapping_vf2pp(exec, subclass_mappings[i][0][0], object_mapping)
                            else:
                                is_isomorphic = _isomorphism_under_object_mapping(exec,
                                                                                        subclass_mappings[i][0][0],
                                                                                        object_mapping)
                            if is_isomorphic:
                                subclass_mappings[subclass_counter].append(
                                    (exec, case_id))
                                found = True
                                break


                        if found:
                            break
            if (time.time() - start_time) > timeout:
                return None, None, None, None, -1
                raise Exception("timeout")
            if found:
                continue
            subclass_counter += 1
            subclass_mappings[subclass_counter] = [(exec, case_id)]

        for ind in subclass_mappings.keys():
            variants_dict[_class + str(ind)] = [case_id for (exec,
                                                             case_id) in subclass_mappings[ind]]
            (exec, case_id) = subclass_mappings[ind][0]
            variant_graphs[_class +
                           str(ind)] = (exec, ocel.process_execution_objects[case_id])
        del variants_dict[_class]
        del variant_graphs[_class]

    variant_frequencies = {
        v: len(variants_dict[v]) / len(ocel.process_executions) for v in variants_dict.keys()}
    variants, v_freq_list = map(list,
                                zip(*sorted(list(variant_frequencies.items()), key=lambda x: x[1], reverse=True)))
    variant_event_map = {}
    for v_id in range(0, len(variants)):
        v = variants[v_id]
        cases = [ocel.process_executions[c_id] for c_id in variants_dict[v]]
        events = set().union(*cases)
        for e in events:
            if e not in variant_event_map.keys():
                variant_event_map[e] = []
            variant_event_map[e] += [v_id]
    ocel.log.log["event_variant"] = ocel.log.log["event_id"].map(variant_event_map)
    ocel.log.log.drop('event_objects', axis=1, inplace=True)
    return variants, v_freq_list, variant_graphs, variants_dict, time.time() - s_time