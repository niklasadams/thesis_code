from ocpa.algo.conformance.precision_and_fitness.variants import replay_context
import ocpa.algo.conformance.precision_and_fitness.utils as utils

REPLAY_CONTEXT = "replay_context"
VERSIONS = {REPLAY_CONTEXT:replay_context.calculate}


def apply(ocel,ocpn,version = REPLAY_CONTEXT, contexts=None,bindings=None):
    '''
    Calculation precision and fitness for an object-centric Petri net with respect to an object-centric event log. The
    measures are calculated according to replaying the event log and checking enabled and executed behavior. Contexts and
    bindings can be pre-computed and passed to the method to save computation time upon multiple calling. If not given,
    contexts and binding wil be calculated.

    :param ocel: Object-centric event log
    :type ocel: :class:`OCEL <ocpa.objects.log.ocel.OCEL>`

    :param ocpn: Object-centric Petri net
    :type ocpn: :class:`OCPN <ocpa.objects.oc_petri_net.obj.ObjectCentricPetriNet>`

    :param contexts: multiset of previously executed traces of activities for each event (can be computed by calling :func:`the corresponding function <ocpa.algo.evaluation.precision_and_fitness.utils.calculate_contexts_and_bindings>`)
    :type contexts: Dict

    :param bindings: bindings for each event (can be computed by calling :func:`the corresponding function <ocpa.algo.evaluation.precision_and_fitness.utils.calculate_contexts_and_bindings>`)
    :type bindings: Dict

    :return: precision, fitness
    :rtype: float, float

    '''

    return VERSIONS[version](ocel,ocpn,contexts,bindings)
    