from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.algo.util.filtering.log import activity_filtering as activity_filtering
from ocpa.algo.conformance.precision_and_fitness import evaluator
import ocpns as ocpns
import pickle
#load the petri net
ocpn, filtered_acts = ocpns.construct_de_jure_net()
print(ocpn)
gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
ocpn_vis_factory.view(gviz)
ocpn_vis_factory.save(gviz, "de_jure_net.svg")

#filter the log to remove all other activities
parameters = {"obj_names": ["application", "offer"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ","}
ocel = ocel_import_factory.apply(file_path="../../sample_logs/csv/BPI2017-Final.csv", parameters=parameters)
filtered_ocel = activity_filtering.filter_activities(ocel,filtered_acts)
print(len(filtered_ocel.variants))
print(len(filtered_ocel.process_executions))
print(len(filtered_ocel.log.log))


#compute the fitness of the process executions
precision, fitness, skipped_events, L_c, M_c = evaluator.apply(filtered_ocel,ocpn)
results = {"precision":precision,"fitness":fitness,"L_c":L_c,"M_c":M_c}
with open('results.pickle', 'wb') as file:
    b = pickle.dump(results,file)

