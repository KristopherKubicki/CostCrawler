
import json
import sqlalchemy as sa 
import geoalchemy2 

from sqlalchemy.ext.declarative import declarative_base
from uszipcode import Zipcode, SearchEngine
from tldextract import extract

from func import db, facility


Base = declarative_base()

class Facility(Base):
    __tablename__ = 'facility'

    facility_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)
    _display_name = sa.Column('display_name', sa.String(256), nullable=False)
    location = sa.Column(geoalchemy2.Geometry('POINT'), nullable=False)
    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    edit_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    scrape_time = sa.Column(sa.DateTime, nullable=True)
    _scrape_json = sa.Column('scrape_results', sa.String(), nullable=True)
    address = sa.Column('address', sa.String(256), nullable=True)
    postal_code = sa.Column(sa.String(8), nullable=True)
    phone = sa.Column(sa.String(18), nullable=True)

    homepage = sa.Column('homepage', sa.String(256), nullable=True)
    pricepage = sa.Column('pricepage', sa.String(256), nullable=True)
    pricelist = sa.Column('pricelist', sa.String(256), nullable=True)
    population = sa.Column('population', sa.Integer, nullable=False, default=0)

    latitude = sa.orm.column_property(sa.func.ST_X(location))
    longitude = sa.orm.column_property(sa.func.ST_Y(location))

    raw_charges = sa.orm.relationship("RawCharge")

    @property
    def raw_procedures(self):
        lraw_procedures = []
        for lraw_charge in sorted(self.raw_charges, key=lambda x: x.charge, reverse=True):
            if lraw_charge.raw_procedure and lraw_charge.raw_procedure not in lraw_procedures:
                lraw_procedures.append(lraw_charge.raw_procedure)
        return lraw_procedures

    @property
    def true_procedures(self):
        ltrue_procedures = []
        for lraw_procedure in sorted(self.raw_procedures, key=lambda x: x.description):
            if lraw_procedure.true_procedure and lraw_procedure.true_procedure not in ltrue_procedures:
                ltrue_procedures.append(lraw_procedure.true_procedure)
        return ltrue_procedures

    @property
    def agg_procedures(self):
        lagg_procedures = []
        for ltrue_procedure in sorted(self.true_procedures, key=lambda x: x.hcpc_code):
            if ltrue_procedure.agg_procedure and ltrue_procedure.agg_procedure not in lagg_procedures:
                lagg_procedures.append(ltrue_procedure.agg_procedure)
        return lagg_procedures

    @property
    def scrape_json(self):
        if self._scrape_json:
            ltags = None
            if type(self._scrape_json) == dict:
                return self._scrape_json
            try:
                ltags = json.loads(self._scrape_json)
            except Exception as e:
                print("json loading error:", type(self._scrape_json), self._scrape_json, e)
            return ltags
        return {}

    @scrape_json.setter
    def scrape_json(self, value):
        try:
            self._scrape_json = json.dumps(value, default=str, sort_keys=True,indent=4, separators=('\n,', ': '))

        except Exception as e:
            print("scrape json setting error:", self._scrape_json)


    @property
    def nearby_zips(self):
        if self.scrape_json and self.scrape_json.get('nearby_zips'):
            return self.scrape_json['nearby_zips']

    @property
    def keywords(self):
        if self.scrape_json and self.scrape_json.get('result') and self.scrape_json['result'].get('types'):
            return ', '.join(self.scrape_json['result']['types'])

    @property
    def pricepages(self):
        if self.scrape_json and self.scrape_json.get('pricepages'):
            return self.scrape_json['pricepages']

    @property
    def pricelists(self):
        if self.scrape_json and self.scrape_json.get('pricelists'):
            return self.scrape_json['pricelists']

    @property
    def domain(self):
        if self.homepage:
            tsd, td, tsu = extract(self.homepage)
            return td + '.' + tsu

    @property
    def display_name(self):
        if self._display_name:
            return self._display_name.title()
        return self.name.title()

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def healthy(self):
        if self.homepage and self.scrape_time and len(self.raw_charges) > 0:
            return True
        return False

class Network():
    
    facilities = []
    true_procedures = []

    @property
    def facility_ids(self):
        lids = []
        for lfac in self.facilities:
            lids.append(lfac.facility_id)
        return lids

    @property
    def raw_charges(self):
        lcharges = []
        for lfac in self.facilities:
            for lcharge in lfac.raw_charges:
                if lcharge not in lcharges:
                    lcharges.append(lcharge)
        return lcharges

    @property
    def raw_procedures(self):
        lprocedures = []
        for lfac in self.facilities:
            for lproc in lfac.raw_procedures:
                if lproc not in lprocedures:
                    lprocedures.append(lproc)
        return lprocedures

    @property
    def true_procedures(self):
        lprocedures = []
        for lfac in self.facilities:
            for lproc in lfac.true_procedures:
                if lproc not in lprocedures:
                    lprocedures.append(lproc)
        return lprocedures

    @property
    def agg_procedures(self):
        lprocedures = []
        for lfac in self.facilities:
            for lproc in lfac.agg_procedures:
                if lproc not in lprocedures:
                    lprocedures.append(lproc)
        return lprocedures

    @property
    def agg_procedure_cost(self, agg_procedure):
        lcharges = []
        lmin, lmax, lavg = None, None, None
        for tagg in agg_procedure.true_procedures:
            for ragg in tagg.raw_procedures:
                for cagg in ragg.raw_charges:
                    if cagg.facility_id in self.facility_ids:
                        lcharges.append(cagg.charge)
        print("lcharges:", lcharges)
            



class Zone(Base):
    __tablename__ = 'zone'

    zone_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    location = sa.Column(geoalchemy2.Geometry('POINT'), nullable=False)
    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    state = sa.Column('state',sa.String(2), nullable=False)
    type = sa.Column('type',sa.String(3), nullable=False)

    latitude = sa.orm.column_property(sa.func.ST_X(location))
    longitude = sa.orm.column_property(sa.func.ST_Y(location))
    facility_count = sa.Column('facility_count', sa.Integer(), nullable=False, default=0)
    charge_count = sa.Column('charges_count', sa.Integer(), nullable=False, default=0)
    population = sa.Column('population', sa.Integer(), nullable=False, default=0)
    density = sa.Column('density', sa.Integer(), nullable=False, default=0)

    # TODO: rewrite this with a relationshp instead
    #https://docs.sqlalchemy.org/en/13/orm/join_conditions.html#custom-operators-based-on-sql-functions
    @property
    def facilities(self, dist=0.3):
        rets = db.session.execute('SELECT facility_id FROM facility WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326), %.2f)' % (self.latitude, self.longitude, dist));
        lfacilities = []
        lcount = 0
        for ret in rets:
            lcount += 1
            lfacility = facility.get_facility_by_id(ret[0])
            if lfacility:
                lfacilities.append(lfacility)
        if lcount != self.facility_count:
            self.facility_count = lcount
            db.session.commit()
        return lfacilities

    _city = None
    @property
    def city(self):
        if self._city:
            return self._city
        if self.usz_simple and self.usz_simple[0].common_city_list:
            if len(self.usz_simple[0].common_city_list) == 1:
                self._city = '%s' % self.usz_simple[0].common_city_list[0]
            else:
                self._city = '%s, %s' % (self.usz_simple[0].common_city_list[0], self.usz_simple[0].common_city_list[1])
        else:
            self._city = ''
        return self._city 

    @property
    def area(self):
        if self.usz_simple and self.usz_simple[0].area_code_list:
            return ', '.join(self.usz_simple[0].area_code_list)
        return ''

    @property
    def county(self):
        if self.usz_simple and self.usz_simple[0].county:
            return self.usz_simple[0].county

    @property
    def usz_simple(self):
       search = SearchEngine(simple_zipcode=True)
       usz = search.by_coordinates(self.latitude, self.longitude, radius=30, returns=1)
       return usz

    @property
    def usz(self):
       search = SearchEngine(simple_zipcode=False)
       usz = search.by_coordinates(self.latitude, self.longitude, radius=30, returns=1)
       return usz

    @property
    def zips(self):
       search = SearchEngine(simple_zipcode=False)
       zips = []
       for lzip in search.by_coordinates(self.latitude, self.longitude, radius=30, returns=7):
           zips.append(lzip.zipcode)
       return zips




class AggProcedure(Base):
    __tablename__ = 'agg_procedure'

    agg_procedure_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(), nullable=False)
    live = sa.Column(sa.Boolean, nullable=False, default=False)
    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    live_time = sa.Column(sa.DateTime, nullable=True)

    true_procedure = sa.orm.relationship("TrueProcedure")

    @property
    def true_procedure_count(self):
        return len(self.true_procedure)

    @property
    def average_charge(self):
        llen = 0
        ltot = 0
        for tp in self.true_procedure:
            llen += 1
            ltot += tp.average_charge
        if llen > 0:
            return ltot / llen
        return 0

    def local_average_charge(self, facilities):

        llen = 0
        ltot = 0
        for rp in self.true_procedure:
            lret = rp.local_average_charge(facilities)
            if lret > 0:
                ltot += lret
                llen += 1
        if llen > 0:
            return ltot / llen
        return 0

    def local_lowest_charge(self, facilities):

        fids = []
        for f in facilities:
            fids.append(f.facility_id)

        ltot = None
        for rp in self.true_procedure:
          rc = rp.local_lowest_charge(facilities) # todo: recent_raw_charge
          if rc:
            if rc.facility_id not in fids or not rc.charge or rc.live is False:
                continue
            if ltot is None or ltot.charge > rc.charge:
                ltot = rc
        return ltot


class TrueProcedure(Base):
    __tablename__ = 'true_procedure'

    true_procedure_id = sa.Column(sa.Integer, primary_key=True)
    agg_procedure_id = sa.Column(sa.Integer, sa.ForeignKey('agg_procedure.agg_procedure_id'),  nullable=True)
    name = sa.Column(sa.String(), nullable=False)
    _display_name = sa.Column('display_name',sa.String(128), nullable=True)
    hcpc_code = sa.Column(sa.String(), nullable=False)
    raw_procedure_count = sa.Column(sa.Integer, nullable=False, default=0)
    description = sa.Column(sa.String())
    reasons = sa.Column('reason', sa.String(), nullable=True)
    anatomy = sa.Column('anatomy', sa.String(256), nullable=True)
    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    map_time = sa.Column(sa.DateTime)

    agg_procedure = sa.orm.relationship("AggProcedure")
    raw_procedure = sa.orm.relationship("RawProcedure")

    @property
    def display_name(self):
        if self._display_name:
            return self._display_name
        return self.name.title()

    @property
    def average_charge(self):
        llen = 0
        ltot = 0
        for rp in self.raw_procedure:
            llen += 1
            ltot += rp.average_charge
        if llen > 0:
            return ltot / llen
        return 0

    def local_average_charge(self, facilities):

        llen = 0
        ltot = 0
        for rp in self.raw_procedure:
            lret = rp.local_average_charge(facilities)
            if lret > 0:
                ltot += lret
                llen += 1
        if llen > 0:
            return ltot / llen
        return 0


    def local_lowest_charge(self, facilities):

        fids = []
        for f in facilities:
            fids.append(f.facility_id)

        ltot = None
        for rp in self.raw_procedure:
            rc = rp.local_lowest_charge(facilities) # todo: recent_raw_charge
            if rc:
                if rc.facility_id not in fids or not rc.charge or rc.live is False or rc.charge < 200:
                    continue
                if ltot is None or ltot.charge > rc.charge:
                    ltot = rc
        return ltot



class RawProcedure(Base):
    __tablename__ = 'raw_procedure'

    raw_procedure_id = sa.Column(sa.Integer, primary_key=True)
    true_procedure_id = sa.Column(sa.Integer, sa.ForeignKey('true_procedure.true_procedure_id'), nullable=True)
    bill_id = sa.Column(sa.String(32), nullable=True)
    description = sa.Column(sa.String(64), nullable=True)
    live = sa.Column(sa.Boolean, nullable=False, default=True)
    raw_charge_count = sa.Column(sa.Integer, nullable=False, default=0)

    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    map_time = sa.Column(sa.DateTime, nullable=True)
    live_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())

    true_procedure = sa.orm.relationship("TrueProcedure")
    raw_charge = sa.orm.relationship("RawCharge")
    
    @property
    def average_charge(self):
        llen = 0
        ltot = 0
        for rc in self.raw_charge:
            if rc.live is True and rc.charge > 200:
                llen += 1
                ltot += rc.charge
        if llen > 0:
            return ltot / llen
        return 0

    def local_average_charge(self, facilities):

        fids = []
        for f in facilities:
            fids.append(f.facility_id)

        llen = 0
        ltot = 0
        for rc in self.raw_charge: # todo: recent_raw_charge
            if rc.facility_id not in fids or not rc.charge or rc.live is False or rc.charge < 200:
                continue
            llen += 1
            ltot += rc.charge
        if llen > 0:
            return ltot / llen
        return 0

    def local_lowest_charge(self, facilities):

        fids = []
        for f in facilities:
            fids.append(f.facility_id)

        ltot = None
        for rc in self.raw_charge: # todo: recent_raw_charge
            if rc.facility_id not in fids or not rc.charge or rc.live is False or rc.charge < 200:
                continue
            if ltot is None or ltot.charge > rc.charge:
                ltot = rc
        return ltot




class RawCharge(Base):
    __tablename__ = 'raw_charge'

    raw_charge_id = sa.Column(sa.Integer, primary_key=True)
    raw_procedure_id = sa.Column(sa.Integer, sa.ForeignKey('raw_procedure.raw_procedure_id'), nullable=False)
    facility_id = sa.Column(sa.Integer, sa.ForeignKey('facility.facility_id'), nullable=False)
    charge_type = sa.Column(sa.String(3), nullable=False, default='CM')
    charge = sa.Column(sa.Numeric(10,2), nullable=False)
    live = sa.Column(sa.Boolean, nullable=False, default=True)

    scrape_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    creation_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    live_time = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
   
    raw_procedure = sa.orm.relationship("RawProcedure")
    facility = sa.orm.relationship("Facility")


