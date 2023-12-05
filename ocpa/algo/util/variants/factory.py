from ocpa.algo.util.variants.versions import onephase
from ocpa.algo.util.variants.versions import twophase
from ocpa.algo.util.variants.versions import naive
from ocpa.util.constants import TWO_PHASE, ONE_PHASE, NAIVE_MAPPING

VERSIONS = {TWO_PHASE: twophase.apply,
            ONE_PHASE: onephase.apply,
            NAIVE_MAPPING: naive.apply}


def apply(ocel, variant=TWO_PHASE, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
