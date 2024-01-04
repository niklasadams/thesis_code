from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
from ocpa.objects.log.importer.csv import factory as ocel_import_factory
from ocpa.algo.util.filtering.log import activity_filtering as activity_filtering
from ocpa.algo.conformance.precision_and_fitness import evaluator
from ocpa.algo.util.noise import events as event_noise
from ocpa.objects.log.util import misc as log_util
import ocpns as ocpns
import pickle
import time
#load the petri net
ocpn, filtered_acts = ocpns.construct_de_jure_net()
#filter the log to remove all other activities
parameters = {"obj_names": ["application", "offer"],
                        "val_names": [],
                        "act_name": "event_activity",
                        "time_name": "event_timestamp",
                        "sep": ","}
ocel = ocel_import_factory.apply(file_path="../../sample_logs/csv/BPI2017-Final.csv", parameters=parameters)
filtered_ocel_ = activity_filtering.filter_activities(ocel,filtered_acts)
results_dict = {}
for noise_level in [i*0.01 for i in range(1,10)]:
    #conduct experiments 5 times for each noise level to average out the differences
    for _ in range(0,5):
        allowed_switches = {
            "offer":[("Accept offer","Cancel offer"),("Call","Mail")],
            "application":[("Create offer","Cancel application"), ("Submit","Withdraw")]
        }
        filtered_ocel = event_noise.switch_activities(filtered_ocel_,noise_level,allowed_switches=allowed_switches)
        s_time = time.time()
        precision, fitness, skipped_events, L_c, M_c = evaluator.apply(filtered_ocel,ocpn)
        oc_time = time.time() - s_time
        results_dict.setdefault(("oc",noise_level),[])
        results_dict[("oc",noise_level)].append({"precision":precision,"fitness":fitness, "time":oc_time, "skipped_events": skipped_events})
        print("OC, "+str(noise_level))
        print({"precision":precision,"fitness":fitness, "time":oc_time, "skipped_events": skipped_events})
        flat_fits = []
        flat_precs = []
        flat_skipped = []
        s_time = time.time()
        for ot in filtered_ocel.object_types:
            fl_log = log_util.flatten_log(filtered_ocel,ot)
            ocpn_1 = ocpn.flatten_to_type(ot)
            precision, fitness, skipped_events, L_c, M_c = evaluator.apply(fl_log,ocpn_1)
            flat_fits.append(fitness)
            flat_precs.append(precision)
            flat_skipped.append(skipped_events)
        fitness = sum(flat_fits)/len(flat_fits)
        precision = sum(flat_precs)/len(flat_precs)
        skipped_events = sum(flat_skipped)/len(flat_skipped)
        flat_time = time.time() - s_time
        results_dict.setdefault(("flat",noise_level),[])
        results_dict[("flat", noise_level)].append({"precision": precision, "fitness": fitness, "time":flat_time, "skipped_events": skipped_events})
        print("Flat, "+str(noise_level))
        print({"precision":precision,"fitness":fitness, "time":flat_time, "skipped_events": skipped_events})
with open('comparison_10.pickle', 'wb') as file:
    b = pickle.dump(results_dict,file)

