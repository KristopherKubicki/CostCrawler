
import sqlalchemy as sa
import re
from func import db, model

def string_to_zone(lc):

    lc = re.sub(r'[^\x00-\x7F]','', lc)
    lc = lc.strip().lower().replace('_',' ')

    return db.session.query(model.Zone).filter(sa.func.lower(model.Zone.name) == lc).first()


def get_zones_by_ids(zone_ids):
    return db.session.query(model.Zone).filter(model.Zone.zone_id.in_(zone_ids)).all()

def get_zone_by_id(zone_id):
    return db.session.query(model.Zone).filter(model.Zone.zone_id == zone_id).first()
