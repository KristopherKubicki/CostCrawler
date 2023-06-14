
import datetime

from fuzzywuzzy import fuzz
from func import custom, db, model, parser

#whitelist = ['mri','ct','x-ray']
whitelist = ['mri']

def create_procedure(bill_id, description):

    raw_procedure = check_procedure(bill_id, description)
    if raw_procedure is None:

        if whitelist:
            wl = False
            for w in whitelist:
                if w in description.lower():
                    wl = True
                    break
            if not wl:
                return

        raw_procedure = model.RawProcedure()
        raw_procedure.bill_id = bill_id
        raw_procedure.description = description
        db.session.add(raw_procedure)
        db.session.commit()

        update_identical(raw_procedure.raw_procedure_id)

    return raw_procedure
    
def check_procedure(bill_id, description):

    return db.session.query(model.RawProcedure).filter(model.RawProcedure.bill_id == bill_id).filter(model.RawProcedure.description == description).first()


def update_identical(raw_procedure_id=None):

    if raw_procedure_id:
        raw_procedures = db.session.query(model.RawProcedure).filter(model.RawProcedure.raw_procedure_id == raw_procedure_id).all()
    else:
        raw_procedures = db.session.query(model.RawProcedure).filter(model.RawProcedure.true_procedure_id == None).all()

    true_procedures = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.agg_procedure_id != None).all()

    true_names = {}
    tpd = {}
    for tp in true_procedures:
        true_names[tp.true_procedure_id] = custom.mri_smoother(tp.name)
        tpd[tp.true_procedure_id] = tp

    (found,counted) = (0,0)
    for rp in raw_procedures:
        ld = custom.mri_smoother(rp.description)
        counted += 1

        print("rp:", rp.description, "ld:", ld)
        cands = {}
        for tn in true_names:
            fratio = fuzz.token_sort_ratio(ld, true_names[tn])
            if fratio < 50:
                fratio = fuzz.partial_ratio(ld, true_names[tn])
                if fratio < 50:
                    fratio = fuzz.ratio(ld, true_names[tn])
            fratio += parser.kw_booster(ld, true_names[tn], key_words = ['w/o',' wo ','without','w-o'])

            if fratio > 70:
                cands[tn] = fratio

        lfound = False
        for cand in sorted(cands, key=lambda x: cands[x], reverse=True):
            print("   cand:", cands[cand], cand, true_names[cand])
            lfound = True
            rp.true_procedure_id = cand
            rp.map_time = datetime.datetime.utcnow()
            tpd[cand].raw_procedure_count += 1
            db.session.commit()
            found += 1
            break

        if lfound:
            continue

        if rp.bill_id:
            lps = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.hcpc_code == rp.bill_id).order_by(model.TrueProcedure.creation_time).all()
            for lp in lps:
                print("   np:", lp.hcpc_code, lp.name)
                rp.true_procedure_id = lp.true_procedure_id
                lp.raw_procedure_count += 1
                lp.map_time = datetime.datetime.utcnow()
                db.session.commit()
                found += 1
    print("raw:", raw_procedure_id, "found:", found, "counted:", counted)
    return found


# todo: enrich a procedure with db inforrmation
# http://bioportal.bioontology.org/ontologies/CPT?p=classes&conceptid=74181
