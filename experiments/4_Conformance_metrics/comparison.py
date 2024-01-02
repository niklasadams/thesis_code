from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.algo.util.filtering.log import activity_filtering as activity_filtering
from ocpa.algo.conformance.precision_and_fitness import evaluator
from ocpa.algo.util.noise import events as event_noise
from ocpa.objects.log.util import misc as log_util
import ocpns as ocpns
import pickle
#load the petri net
ocpn, filtered_acts = ocpns.construct_de_jure_net()
#filter the log to remove all other activities
parameters = {"obj_names": ["application", "offer"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ","}
ocel = ocel_import_factory.apply(file_path="../../sample_logs/csv/BPI2017-smp.csv", parameters=parameters)
filtered_ocel_ = activity_filtering.filter_activities(ocel,filtered_acts)
noise_level = 1
allowed_switches = {
    "offer":[("Accept offer","Cancel offer")]
}
filtered_ocel = event_noise.switch_activities(filtered_ocel_,noise_level,allowed_switches=allowed_switches)
precision, fitness, skipped_events, L_c, M_c = evaluator.apply(filtered_ocel,ocpn)
results = {"precision":precision,"fitness":fitness,"L_c":L_c,"M_c":M_c}
print(results)
print(ocel.object_types[0])
fl1_log = log_util.flatten_log(filtered_ocel,ocel.object_types[0])
print(fl1_log.log.log)
ocpn_1 = ocpn.flatten_to_type(ocel.object_types[0])
ocpn_vis_factory.view(ocpn_vis_factory.apply(ocpn_1, parameters={'format': 'svg'}))
precision, fitness, skipped_events, L_c, M_c = evaluator.apply(fl1_log,ocpn_1)
results = {"precision":precision,"fitness":fitness,"L_c":L_c,"M_c":M_c}
print(results)
print(ocel.object_types[1])
fl2_log = log_util.flatten_log(filtered_ocel,ocel.object_types[1])
print(fl2_log.log.log)
print(len(fl2_log.variants))
print(fl2_log.variants_dict[fl2_log.variants[0]][0])
print(fl2_log.process_executions[fl2_log.variants_dict[fl2_log.variants[0]][0]])
#print([ocelfor e in fl2_log.process_executions[fl2_log.variants_dict[fl2_log.variants[0]][0]]])
ocpn_2 = ocpn.flatten_to_type(ocel.object_types[1])
ocpn_vis_factory.view(ocpn_vis_factory.apply(ocpn_2, parameters={'format': 'svg'}))
precision, fitness, skipped_events, L_c, M_c = evaluator.apply(fl2_log,ocpn_2)
results = {"precision":precision,"fitness":fitness,"L_c":L_c,"M_c":M_c}
print(results)

    #In each iteration, randomly introduce some noise

    #flatten the event log

    #calculate both fitnesses