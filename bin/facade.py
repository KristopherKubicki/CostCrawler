#!/usr/bin/env python3

import sqlalchemy
import requests
import validators
import pandas as pd
import json

from statistics import median

from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import make_response

from uszipcode import Zipcode, SearchEngine

from func import charge, config, db, facility, model, parser, zone

app = Flask(__name__)

loc = '60712'

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/facility/<int:facility_id>/rescan", endpoint='facility_page_rescan', methods=['POST'])
def facility_page_rescan(facility_id):

    lfacility = db.session.query(model.Facility).filter(model.Facility.facility_id == facility_id).first()
    facility.scrape_facility(lfacility)

    return render_template("facility_detail.html", facility=lfacility)

@app.route("/facility/<int:facility_id>", endpoint='facility_page', methods=['GET', 'POST'])
def facility_page(facility_id):

    lfacility = db.session.query(model.Facility).filter(model.Facility.facility_id == facility_id).first()
    if request.method == "POST":
        llines = []

# TODO: detect robots.txt and incapsula

        price_list = False
        if request.form['text']:
            first_line = request.form['text'].splitlines()[0]
            print("first:", first_line)
            if first_line and validators.url(first_line):
                r = requests.get(first_line, allow_redirects=True)
                print("first?:", first_line, r.status_code, len(r.text))
                if r and r.content:
                    try:
                        read_file = pd.read_excel(r.content)
                        llines = read_file.to_csv(index=False).splitlines()
                        if len(llines) > 0:
                            facility.price_list = first_line
                    except Exception as e:
                        if r.text:
                            llines = r.text.splitlines()
                            if len(llines) > 0:
                                facility.price_list = first_line
                    db.session.commit()
                elif r and r.text:
                    llines = r.text.splitlines()
                    if len(llines) > 0:
                        facility.price_list = first_line
            else:
                llines = request.form['text'].splitlines()
        elif request.files['file']:
            # TODO: tell if this is a csv or an xls
            lbytes = request.files['file'].read()
            try:
                read_file = pd.read_excel(lbytes)
                llines = read_file.to_csv(index=False).splitlines()
                print("FOUND:", len(llines))
                if len(llines) == 0:
                    llines = lbytes.decode().splitlines()
            except Exception as e:
                print("not an excel file!:", len(lbytes))
                llines = lbytes.decode().splitlines()


        for line in llines:
            if parser.service_filter(line):
                print("line:", line)
                pcharge = parser.line_to_charge(line)
                if pcharge[1] is not None and pcharge[2] is not None:
                    ret = charge.create_charge(facility_id, pcharge[0], pcharge[1], pcharge[2])

        db.session.commit()

    return render_template("facility_detail.html", facility=lfacility)

@app.route("/facility/", endpoint='facility_home')
def lfacility():


    network = model.Network()
    network.facilities = []
    network.facilities = db.session.query(model.Facility).order_by(model.Facility.population.desc()).all()
    
    return render_template("facility.html", network=network)

@app.route("/raw_charge/", endpoint='raw_charge_home')
def raw_charge():
    raw_charges = db.session.query(model.RawCharge).all()
    return render_template("raw_charge.html", raw_charges=raw_charges)

@app.route("/raw_charge/<int:raw_charge_id>", endpoint='raw_charge_page')
def raw_charge(raw_charge_id):
    raw_charges = db.session.query(model.RawCharge).filter(model.RawCharge.raw_charge_id == raw_charge_id).all()
    return render_template("raw_charge.html", raw_charges=raw_charges)

@app.route("/raw_procedure/<int:raw_procedure_id>", endpoint='raw_procedure_page')
def raw_procedure(raw_procedure_id):
    raw_procedure = db.session.query(model.RawProcedure).filter(model.RawProcedure.raw_procedure_id == raw_procedure_id).first()
    raw_charges = db.session.query(model.RawCharge).filter(model.RawCharge.raw_procedure_id == raw_procedure_id).order_by(model.RawCharge.creation_time.desc()).all()
    return render_template("raw_charge.html", raw_charges=raw_charges, raw_procedure=raw_procedure)

@app.route("/raw_procedure/", endpoint='raw_procedure_home')
def raw_procedure():
    raw_procedures = db.session.query(model.RawProcedure).all()
    return render_template("raw_procedure.html", raw_procedures=raw_procedures)

@app.route("/procedures", endpoint='true_procedure_search', methods=['POST'])
def true_procedure_search():

    search_term = request.form['search']
    search_term = search_term.strip()
    # TODO: scrub
    # TODO: redirect hcpc hit

    true_procedures = []
    if search_term.isnumeric():
        query = "SELECT true_procedure_id FROM true_procedure WHERE true_procedure.hcpc_code = '%d'" % (int(search_term))
        rets = db.session.execute(query)
        for ret in rets:
           true_procedure = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.true_procedure_id == ret[0]).first()
           if true_procedure:
               true_procedures.append(true_procedure)

    if len(true_procedures) == 0:
        query = "SELECT true_procedure_id FROM true_procedure WHERE true_procedure.description ilike '%%%s%%' or name ilike '%%%s%%' or reason ilike '%%%s%%' order by raw_procedure_count desc" % (search_term, search_term, search_term)
        rets = db.session.execute(query)
        for ret in rets:
           true_procedure = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.true_procedure_id == ret[0]).first()
           if true_procedure:
               true_procedures.append(true_procedure)
    if len(true_procedures) == 1:
        zone_id = request.form['location']
        lzone = zone.string_to_zone(zone_id)
        print("render true:", true_procedures)
        network = model.Network()
        network.facilities = lzone.facilities
        return render_template("true_procedure_detail.html", true_procedure=true_procedures[0], network=network)
    return render_template("true_procedure.html", true_procedures=true_procedures)


@app.route("/true_procedure/", endpoint='true_procedure_home')
def true_procedure():
    true_procedures = db.session.query(model.TrueProcedure).order_by(model.TrueProcedure.hcpc_code).all()

    return render_template("true_procedure.html", true_procedures=true_procedures)

@app.route("/true_procedure/<int:true_procedure_id>", endpoint='true_procedure_update', methods=['POST'])
def true_procedure_update(true_procedure_id):

    true_procedure = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.true_procedure_id == true_procedure_id).first()

    ltitle = request.form['title']
    if ltitle:
        true_procedure._display_name = ltitle

    ltitle = request.form['reasons']
    if ltitle:
        true_procedure.reasons = ltitle

    ltitle = request.form['anatomy']
    if ltitle:
        true_procedure.anatomy = ltitle
    db.session.commit()

    network = model.Network()
    zone_id = request.cookies.get('zone')
    if zone_id:
        lzone = zone.string_to_zone(zone_id)
        network.facilities = lzone.facilities
    return render_template("true_procedure_detail.html", true_procedure=true_procedure, network=network)

@app.route("/true_procedure/<int:true_procedure_id>", endpoint='true_procedure_page')
def true_procedure(true_procedure_id):
    true_procedure = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.true_procedure_id == true_procedure_id).first()
    #raw_procedures = db.session.query(model.RawProcedure).filter(model.RawProcedure.true_procedure_id == true_procedure_id).order_by(model.RawProcedure.bill_id,model.RawProcedure.description).all()
    #return render_template("raw_procedure.html", raw_procedures=raw_procedures, true_procedure=true_procedure)

    network = model.Network()
    zone_id = request.cookies.get('zone')
    if zone_id:
        lzone = zone.string_to_zone(zone_id)
        network.facilities = lzone.facilities

    return render_template("true_procedure_detail.html", true_procedure=true_procedure, network=network)


@app.route("/agg_procedure/", endpoint='agg_procedure_home')
def agg_procedure():
    agg_procedures = db.session.query(model.AggProcedure).all()
    return render_template("agg_procedure.html", agg_procedures=agg_procedures)

@app.route("/agg_procedure/<int:agg_procedure_id>", endpoint='agg_procedure_page')
def agg_procedure(agg_procedure_id):
    agg_procedure = db.session.query(model.AggProcedure).filter(model.AggProcedure.agg_procedure_id == agg_procedure_id).first()
    true_procedures = db.session.query(model.TrueProcedure).filter(model.TrueProcedure.agg_procedure_id == agg_procedure_id).order_by(model.TrueProcedure.hcpc_code).all()
    return render_template("true_procedure.html", true_procedures=true_procedures, agg_procedure=agg_procedure)

@app.route('/zone', methods=['POST'])
def zone_search():

    zone_id = request.form['location']
    lzone = zone.string_to_zone(zone_id)
    print("searching lzone?:", lzone)
    if not lzone:
        search = SearchEngine(simple_zipcode=True)
        lzip = search.by_zipcode(zone_id)
        if not lzip:
           print("searching byzip code:", zone_id)
           lzipr = search.by_city_and_state(zone_id, "IL")
           if len(lzipr) > 0:
               lzip = lzipr[0]
        if not lzip or not lzip.lat or not lzip.lng:
            print("TODO: not available yet")
            return render_template("no_zone.html")

        dist = 0.3
        rets = db.session.execute('SELECT zone_id, ST_Distance(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326)) as dist FROM zone WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326), %.2f) order by dist asc, population desc limit 1' % (lzip.lat, lzip.lng, lzip.lat, lzip.lng, dist))
        for lret in rets:
            lzone = zone.get_zone_by_id(lret[0])
 
    if lzone:
        response = make_response(redirect("/zone/%s" % lzone.name, code=302))
        response.set_cookie('zone', lzone.name)
        return response
    return render_template("no_zone.html")

@app.route("/zone/")
def lzone():
    zones = db.session.query(model.Zone).filter(model.Zone.type == "CIT").filter(model.Zone.facility_count > 10).order_by(model.Zone.density.desc()).limit(20).all()
    return render_template("zone.html", zones=zones)

@app.route("/zone/json")
def zzone():
    lzones = db.session.query(model.Zone).filter(model.Zone.type == "CIT").filter(model.Zone.facility_count > 10).order_by(model.Zone.density.desc()).limit(20).all()

    qzones = []
    for lzone in lzones:
        fzone = {}
        fzone['name'] = lzone.name
        fzone['city'] = lzone.city
        fzone['state'] = lzone.state
        fzone['latitude'] = lzone.latitude
        fzone['longitude'] = lzone.longitude

        qzones.append(fzone)


    qjson = json.dumps(qzones, default=str)

    return render_template("zone_export.json", json=qjson)


@app.route("/zone/<string:zone_id>", endpoint='lzone_page')
def lzone_page(zone_id):

    lzone = zone.string_to_zone(zone_id)
    if not lzone:
        search = SearchEngine(simple_zipcode=True)
        lzip = search.by_zipcode(zone_id)
        if not lzip:
           lzipr = search.by_city_and_state(zone_id, "IL")
           if len(lzipr) > 0:
               lzip = lzipr[0]
        if not lzip or not lzip.lat or not lzip.lng:
            print("TODO: not available yet")
            return render_template("no_zone.html")
        dist = 0.3
        rets = db.session.execute('SELECT zone_id, ST_Distance(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326)) as dist FROM zone WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326), %.2f) order by dist asc, population desc limit 1' % (lzip.lat, lzip.lng, lzip.lat, lzip.lng, dist))
        for lret in rets:
            lzone = zone.get_zone_by_id(lret[0])
    if not lzone:
       print("TODO: not available yet")
       return render_template("no_zone.html")


    # todo: transform view by charges
    network = model.Network()
    network.facilities = lzone.facilities

    #return render_template("facility.html", facilities=facilities, network=network)
    return render_template("zone_detail.html", network=network, zone=lzone)

@app.route("/zone/<string:zone_id>/tsv", endpoint='lzone_tsv')
def lzone_txt(zone_id):

    lzone = zone.string_to_zone(zone_id)
    if not lzone:
        search = SearchEngine(simple_zipcode=True)
        lzip = search.by_zipcode(zone_id)
        if not lzip:
           lzipr = search.by_city_and_state(zone_id, "IL")
           if len(lzipr) > 0:
               lzip = lzipr[0]
        if not lzip or not lzip.lat or not lzip.lng:
            print("TODO: not available yet")
            return render_template("no_zone.html")
        dist = 0.3
        rets = db.session.execute('SELECT zone_id, ST_Distance(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326)) as dist FROM zone WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326), %.2f) order by dist asc, population desc limit 1' % (lzip.lat, lzip.lng, lzip.lat, lzip.lng, dist))
        for lret in rets:
            lzone = zone.get_zone_by_id(lret[0])
    if not lzone:
       print("TODO: not available yet")
       return render_template("no_zone.html")


    # todo: transform view by charges
    network = model.Network()
    network.facilities = lzone.facilities

    #return render_template("facility.html", facilities=facilities, network=network)
    lstring = render_template("zone_export.txt", network=network, zone=lzone)
    response = make_response(lstring, 200)
    response.mimetype = "text/plain"
    return response


@app.route("/zone/<string:zone_id>/json", endpoint='lzone_txt')
def lzone_txt(zone_id):

    lzone = zone.string_to_zone(zone_id)
    if not lzone:
        search = SearchEngine(simple_zipcode=True)
        lzip = search.by_zipcode(zone_id)
        if not lzip:
           lzipr = search.by_city_and_state(zone_id, "IL")
           if len(lzipr) > 0:
               lzip = lzipr[0]
        if not lzip or not lzip.lat or not lzip.lng:
            print("TODO: not available yet")
            return render_template("no_zone.html")
        dist = 0.3
        rets = db.session.execute('SELECT zone_id, ST_Distance(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326)) as dist FROM zone WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(%.2f, %.2f), 4326), %.2f) order by dist asc, population desc limit 1' % (lzip.lat, lzip.lng, lzip.lat, lzip.lng, dist))
        for lret in rets:
            lzone = zone.get_zone_by_id(lret[0])
    if not lzone:
       print("TODO: not available yet")
       return render_template("no_zone.html")


    network = model.Network()
    network.facilities = lzone.facilities

    
    ljson = {}
    ljson['data'] = {}
    #ljson['data']['charges'] = []
    ljson['data']['info'] = {}

    ljson['data']['info']['name'] = lzone.name
    ljson['data']['info']['city'] = lzone.city
    ljson['data']['info']['county'] = lzone.county

    ljson['data']['info']['state'] = lzone.state
    ljson['data']['info']['latitude'] = lzone.latitude
    ljson['data']['info']['longitude'] = lzone.longitude
    ljson['data']['info']['zips'] = lzone.zips
    ljson['data']['info']['procedures'] = []

    lfac = []
    for ogg in sorted(network.agg_procedures, key=lambda x: x.name):
        qfac = []
        ze = {}
        ze['prices'] = []
        ze['confirmations'] = 0
        ze['name'] = ogg.name.upper()
        ze['charges'] = []
        for tgg in sorted(ogg.true_procedure, key=lambda x: x.name):
            tfac = []
            # todo: aggregate, min, max, avg
            zo = {}
            zo['facilities'] = {}
            zo['true_procedure_name'] = tgg.name.upper()
            zo['confirmations'] = 0
            zo['code'] = tgg.hcpc_code.strip()
            for agg in tgg.raw_procedure:
                # todo: gets the aggregate price
                for lgg in agg.raw_charge:
                    if lgg.charge < 600 or lgg.charge > 8500:  #TODO
                        continue
                    if lgg.facility.domain == "null" or lgg.facility.domain is None:
                        continue
                    lfac.append(lgg.facility)
                    qfac.append(lgg.facility)
                    tfac.append(lgg.facility)

                    if zo['facilities'].get(lgg.facility.domain) is None:
                        zo['facilities'][lgg.facility.domain] = {}
                        zo['facilities'][lgg.facility.domain]['prices'] = []
                    zo['facilities'][lgg.facility.domain]['prices'].append(lgg.charge)
                    ze['prices'].append(lgg.charge)
                    if zo['facilities'][lgg.facility.domain].get('date') is None or lgg.creation_time < zo['facilities'][lgg.facility.domain]['date']:
                        zo['facilities'][lgg.facility.domain]['date'] = lgg.creation_time
            for dom in sorted(zo['facilities'], key=lambda x: len(zo['facilities'][x]['prices']), reverse=True):
               if len(zo['facilities'][dom]['prices']) > 0:
                   zo['facilities'][dom]['avg'] = median(zo['facilities'][dom]['prices'])
                   zo['facilities'][dom]['min'] = min(zo['facilities'][dom]['prices'])
                   zo['facilities'][dom]['max'] = max(zo['facilities'][dom]['prices'])
                   zo['facilities'][dom]['confirmations'] = len(zo['facilities'][dom]['prices'])
                   zo['confirmations'] += len(zo['facilities'][dom]['prices'])
            allowed = []
            for dom in sorted(zo['facilities'], key=lambda x: zo['facilities'][x]['confirmations'], reverse=True)[:3]:
                allowed.append(dom)
            remove = []
            for dom in sorted(zo['facilities']):
                if dom not in allowed:
                    remove.append(dom)
            for dom in remove:
                if not zo['facilities'].get('others'):
                    zo['facilities']['others'] = {}
                    zo['facilities']['others']['confirmations'] = 0
                    zo['facilities']['others']['date'] = zo['facilities'][dom]['date']
                    zo['facilities']['others']['prices'] = []
                zo['facilities']['others']['prices'].extend(zo['facilities'][dom]['prices'])
                del zo['facilities'][dom]
            if zo['facilities'].get('others'):
                zo['facilities']['others']['confirmations'] = len(zo['facilities']['others']['prices'])
                zo['facilities']['others']['avg'] = median(zo['facilities']['others']['prices'])
                zo['facilities']['others']['min'] = min(zo['facilities']['others']['prices'])
                zo['facilities']['others']['max'] = max(zo['facilities']['others']['prices'])
            for dom in sorted(zo['facilities']):
                del zo['facilities'][dom]['prices']

            if zo['confirmations'] > 1:
                #ljson['data']['charges'].append(zo)
                tfac = list(set(tfac))
                zo['locations'] = len(tfac)
                ze['confirmations'] += zo['confirmations']
                ze['charges'].append(zo)

        ze['avg'] = median(ze['prices'])
        ze['min'] = min(ze['prices'])
        ze['max'] = max(ze['prices'])
        qfac = list(set(qfac))
        ze['locations'] = len(qfac)
        if ze['confirmations'] > 0 and len(ze['prices']) > 0:
            del ze['prices']
            ljson['data']['info']['procedures'].append(ze)

    lfac = list(set(lfac))
    ljson['data']['info']['locations'] = len(lfac)


    qjson = json.dumps(ljson, default=str)

    return render_template("zone_export.json", json=qjson)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
