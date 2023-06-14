
from func import parser


def mri_smoother(left):

    ld = left.lower().strip()
    ld = " " + ld + " "
    ld = parser.smoother(ld, " brst ", " chest ")
    ld = parser.smoother(ld, " brest ", " chest ")
    ld = parser.smoother(ld, "breast", "chest")
    ld = parser.smoother(ld, " head ", " brain ")
    ld = parser.smoother(ld, " contrast ", " dye ")
    ld = parser.smoother(ld, " contr ", " dye ")
    ld = parser.smoother(ld, " cont ", " dye ")
    ld = parser.smoother(ld, " con ", " dye ")
    ld = parser.smoother(ld, "/cont ", "/dye ")
    ld = parser.smoother(ld, " tmj ", " face/neck ")
    ld = parser.smoother(ld, " elbow", " joint upper ")
    ld = parser.smoother(ld, " femur", " lower extremity ")
    ld = parser.smoother(ld, " foot", " lower extremity ")
    ld = parser.smoother(ld, " leg", " lower extremity ")
    ld = parser.smoother(ld, " tib/fib", " lower extremity ")
    ld = parser.smoother(ld, " tibia", " lower extremity ")
    ld = parser.smoother(ld, " fibia", " lower extremity ")
    ld = parser.smoother(ld, " hip", " lower extremity ")
    ld = parser.smoother(ld, " hand", " upper extremity ")
    ld = parser.smoother(ld, " forearm", " upper extremity ")
    ld = parser.smoother(ld, " humerus", " joint upper extremity ")
    ld = parser.smoother(ld, " brachial", " joint upper extremity ")
    ld = parser.smoother(ld, " bracial", " joint upper extremity ")
    ld = parser.smoother(ld, " shoulder", " joint upper extremity ")
    ld = parser.smoother(ld, " wrist", " joint upper extremity ")
    ld = parser.smoother(ld, " knee", " joint lower extremity ")
    ld = parser.smoother(ld, " ankle", " joint lower extremity ")
    ld = parser.smoother(ld, " cervic", " pelvis ")
    ld = parser.smoother(ld, " prostate ", " pelvis ")
    ld = parser.smoother(ld, " sacrum ", " pelvis ")
    ld = parser.smoother(ld, " pituitary", " brain ")
    ld = parser.smoother(ld, " low ", " lower ")
    ld = parser.smoother(ld, " lwr ", " lower ")
    ld = parser.smoother(ld, " upr ", " upper ")
    ld = parser.smoother(ld, " extr ", " extremity ")
    ld = parser.smoother(ld, " extrem ", " extremity ")
    ld = parser.smoother(ld, " ext ", " extremity ")
    ld = ld.strip()

    return ld


