#!/usr/bin/env python3

import os
import time
import datetime

from func import config, db, facility, model

path = config.config['path']

def main():
    with open(os.path.join(path,'data','init','facilities.txt'),"r") as f:
        for line in f.readlines():
            line = line.replace("'","")
            lsplit = line.strip().split('\t')
            loc = lsplit[6].split(', ')

            db.session.execute("insert into facility (facility_id,name,display_name,location,postal_code, address) values ('%d','%s','%s', ST_SetSRID(ST_MakePoint('%.2f','%.2f'),4326), '%s', '%s') on conflict (facility_id) do update set name = '%s', display_name = '%s', location = ST_SetSRID(ST_MakePoint('%.2f','%.2f'),4326), postal_code = '%s', address = '%s'" % 
                    (
                       int(lsplit[0]),lsplit[1],lsplit[1], float(loc[0]), float(loc[1]), lsplit[5], '%s %s, %s, %s' % (lsplit[2], lsplit[3], lsplit[4], lsplit[5]),
                       lsplit[1], lsplit[1], float(loc[0]), float(loc[1]), lsplit[5], '%s %s, %s, %s' % (lsplit[2], lsplit[3], lsplit[4], lsplit[5])
                    ))
            db.session.commit()

    for lfacility in facility.get_all_facilities():
        if not lfacility.scrape_time or lfacility.scrape_time < datetime.datetime.utcnow() - datetime.timedelta(days=30):
            try:
                facility.scrape_facility(lfacility)
            except Exception as e:
                print("exception:", e)
            time.sleep(10)


if __name__ == '__main__':
    main()

