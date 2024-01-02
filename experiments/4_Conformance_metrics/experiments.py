from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.visualization.oc_petri_net import factory as ocpn_vis_factory
import ocpns as ocpns
#load the petri net
ocpn = ocpns.construct_de_jure_net()
print(ocpn)
gviz = ocpn_vis_factory.apply(ocpn, parameters={'format': 'svg'})
ocpn_vis_factory.view(gviz)
ocpn_vis_factory.save(ocpn_vis_factory.apply(ocpn), "de_jure_net.svg")
#filter the log to remove all other activities

#compute the fitness of the process executions
