from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet
from ocpa.objects.oc_petri_net.obj import ObjectCentricPetriNet

def construct_de_jure_net():
    ocpn = ObjectCentricPetriNet(name="BPI2017")
    a = "application"
    o = "offer"
    p1 = ObjectCentricPetriNet.Place(name = "p1", object_type=a, initial= True)
    p2 = ObjectCentricPetriNet.Place(name="p2", object_type=a)
    p3 = ObjectCentricPetriNet.Place(name="p3", object_type=a)
    p4 = ObjectCentricPetriNet.Place(name="p4", object_type=o, initial=True)
    p5 = ObjectCentricPetriNet.Place(name="p5", object_type=a)
    p6 = ObjectCentricPetriNet.Place(name="p6", object_type=o)
    p7 = ObjectCentricPetriNet.Place(name="p7", object_type=o)
    p8 = ObjectCentricPetriNet.Place(name="p8", object_type=a)
    p9 = ObjectCentricPetriNet.Place(name="p9", object_type=a)
    p10 = ObjectCentricPetriNet.Place(name="p10", object_type=a, final= True)
    p11 = ObjectCentricPetriNet.Place(name="p11", object_type=o, final= True)
    [ocpn.places.add(p) for p in [p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11]]

    act1 = "Create application"
    act2 = "Accept"
    act3 = "Create offer"
    act4 = "Call"
    act5 = "Accept offer"
    act6 = "Cancel offer"

    t1 = ObjectCentricPetriNet.Transition(name = act1, label=act1)
    t2 = ObjectCentricPetriNet.Transition(name=act2, label=act2)
    t3 = ObjectCentricPetriNet.Transition(name=act3, label=act3)
    t4 = ObjectCentricPetriNet.Transition(name=act4, label=act4)
    t5 = ObjectCentricPetriNet.Transition(name="Repeat Create", label="", silent=True)
    t6 = ObjectCentricPetriNet.Transition(name=act5, label=act5)
    t7 = ObjectCentricPetriNet.Transition(name=act6, label=act6)
    [ocpn.transitions.add(t) for t in [t1, t2, t3, t4, t5, t6, t7]]

    ocpn.add_arc(ObjectCentricPetriNet.Arc(p1,t1))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t1, p2))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p2, t2))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t2, p3))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p3, t3))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p4, t3))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t5, p3))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t3, p5))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t3, p6))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p5, t4))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p6, t4))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t4, p7))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t4, p8))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p8, t5))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t5, p9))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p7, t6))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p8, t6))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p7, t7))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(p9, t7))
    #ocpn.add_arc(ObjectCentricPetriNet.Arc(p1, t1))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t6, p10))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t6, p11))
    ocpn.add_arc(ObjectCentricPetriNet.Arc(t7, p11))

    return ocpn