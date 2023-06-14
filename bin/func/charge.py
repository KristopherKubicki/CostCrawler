
from func import db, model, numbers, procedure


def create_charge(facility_id, bill_id, description, charge):

    raw_procedure = procedure.create_procedure(bill_id, description)
    if raw_procedure:
        raw_charge = check_charge(facility_id, raw_procedure.raw_procedure_id, charge)
        if not raw_charge:
           raw_charge = model.RawCharge()
           raw_charge.facility_id = facility_id
           raw_charge.raw_procedure_id = raw_procedure.raw_procedure_id
           raw_charge.charge = charge
           db.session.add(raw_charge)
           db.session.commit()
           return raw_charge


def check_charge(facility_id, raw_procedure_id, charge):

    return db.session.query(model.RawCharge).filter(model.RawCharge.facility_id == facility_id).filter(model.RawCharge.raw_procedure_id == raw_procedure_id).first()

