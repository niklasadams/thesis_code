from ocpa.objects.log.importer.ocel import factory as ocel_json_import_factory
from ocpa.objects.log.importer.csv import factory as ocel_csv_import_factory
from ocpa.algo.conformance.execution_extraction import algorithm as extraction_metric_factory
from ocpa.objects.log.exporter.ocel import factory as ocel_export_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP,LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE, NAIVE_MAPPING
import pandas as pd
from ocpa.algo.util.filtering.log import case_filtering
import numpy as np
import re
import os

def compute_variants(param):
    log = param["Log"]
    if "Post-extraction flattening" not in param:
        param["Post-extraction flattening"] = False
    raw_ocel = ocel_json_import_factory.apply("./sublogs/" + log + "_" + str(10) + ".jsonocel", parameters=param)
    i = param["Log Subsize"]
    #print(i)
    # I need to filer on the event log directly to gradually inrease the cases with the ordering preserved
    # This is only for comparison reasons, since the one on one checking is quite sensitive to ordering and
    # will produce inconsistent results
    ocel = case_filtering.filter_process_executions(raw_ocel, cases=raw_ocel.process_executions[
                                                                    0:int(len(raw_ocel.process_executions) * (i / 10))])
    # ocel = ocel_json_import_factory.apply("./sublogs/"+log+"_"+str(i)+".jsonocel", parameters=param)
    computation_time = ocel.variant_computation_time
    comp_type = param["variant_calculation"]
    o_type = None
    if "leading_type" in param.keys():
        o_type = param["leading_type"]
    naive_projection = None
    if "naive_project_object_set" in param.keys():
        naive_projection = True
    extraction_technique = param["execution_extraction"]
    all_objects = set()
    min_o_count, max_o_count = 10000000, 0
    sum_o_counts = 0
    min_e_count, max_e_count = 10000000, 0
    sum_e_counts = 0
    for i in range(0, len(ocel.process_executions)):
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
    hashing_technique = None
    if "hashing_technique" in param.keys():
        hashing_technique = param["hashing_technique"]
    if computation_time == -1:
        individual_results = {
            "Log": log,
            "Number of Events": len(ocel.log.log),
            "Extraction Technique": extraction_technique,
            "Number of Process Executions": len(ocel.process_executions),
            "Variant Computation": comp_type,
            "Hashing Function":hashing_technique,
            "Naive Object String Projection": naive_projection,
            "Number of Variants": -1,
            "Type": o_type,
            "Computation Time": -1,
            "Hashing Time": -1,
            "Validation Time": -1,
            "Average Number of Objects per Execution": sum_o_counts / len(ocel.process_executions),
            "Average Number of Events per Execution": sum_e_counts / len(ocel.process_executions),
            "Number of Object Types": len(ocel.object_types)
        }
    else:
        individual_results = {
            "Log": log,
            "Number of Events": len(ocel.log.log),
            "Extraction Technique": extraction_technique,
            "Number of Process Executions": len(ocel.process_executions),
            "Variant Computation": comp_type,
            "Hashing Function": hashing_technique,
            "Naive Object String Projection": naive_projection,
            "Number of Variants": len(ocel.variants),
            "Type": o_type,
            "Computation Time": computation_time,
            "Hashing Time":ocel.variant_hash_time,
            "Validation Time":ocel.variant_iso_time,
            "Average Number of Objects per Execution": sum_o_counts / len(ocel.process_executions),
            "Average Number of Events per Execution": sum_e_counts / len(ocel.process_executions),
            "Number of Object Types": len(ocel.object_types)
        }
    return individual_results