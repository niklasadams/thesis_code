# from ocpa.objects.oc_petri_net.obj import EnhancedObjectCentricPetriNet
from ocpa.algo.conformance.execution_extraction.versions import set_comparison
from ocpa.objects.log.ocel import OCEL
from typing import Dict


# MODEL_BASED = "model_based"
SET_COMPARISON = "set_comparison"
VERSIONS = {
    SET_COMPARISON: set_comparison.apply
}


def apply(ocel: OCEL, variant=SET_COMPARISON, parameters=None):


    return VERSIONS[variant](ocel, parameters=parameters)
