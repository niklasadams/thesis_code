from ocpa.algo.util.process_executions.versions import connected_components
from ocpa.algo.util.process_executions.versions import leading_type, single_type_flattening
from ocpa.util.constants import CONN_COMP, LEAD_TYPE, SINGLE_FLATTENING

VERSIONS = {CONN_COMP: connected_components.apply,
            LEAD_TYPE: leading_type.apply,
            SINGLE_FLATTENING: single_type_flattening.apply}


def apply(ocel, variant=CONN_COMP, parameters=None):
    return VERSIONS[variant](ocel, parameters=parameters)
