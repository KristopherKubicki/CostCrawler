#!/usr/bin/env python3

import os
from uszipcode import SearchEngine

from func import config, db, model

path = config.config['path']

def main():
    with open(os.path.join(path,'data','init','zone.txt'),"r") as f:
        for line in f.readlines():
            line = line.replace("'","")
            lsplit = line.strip().split('\t')
            if lsplit[0] == 'Zip':
                continue
            ltype = 'CIT'
            if lsplit[0].isnumeric() and len(lsplit[0]) == 5:
                ltype = 'ZIP'

            ldensity = 0
            lpop = 0
            mincome = 0

            print("lsplit[0]:", lsplit[0], line.strip())
            ltz = 'America/Chicago'
            search = SearchEngine(simple_zipcode=False)
            lzip = None
            lret = search.by_coordinates(float(lsplit[3]), float(lsplit[4]), radius=30, returns=1)
            if len(lret) > 0:
                lzip = lret[0]
                ldensity = lzip.population_density
                lpop = lzip.population
                mincome = lzip.median_household_income
                ltz = lzip.timezone

            lstatement = "insert into zone (name,state,type,location,density,population,tz) values ('%s','%s', '%s', ST_SetSRID(ST_MakePoint('%.5f','%.5f'),4326),'%d','%d','%s')" % (lsplit[0], lsplit[2], ltype, float(lsplit[3]), float(lsplit[4]), ldensity, lpop, ltz)
                       
            lstatement += " on conflict (name,state,type) do update set name = '%s', state = '%s', type='%s', location = ST_SetSRID(ST_MakePoint('%.5f','%.5f'),4326), density = '%d', population='%d', tz='%s'" % (lsplit[0], lsplit[2], ltype, float(lsplit[3]), float(lsplit[4]), ldensity, lpop, ltz)

            db.session.execute(lstatement)
            db.session.commit()
   


if __name__ == '__main__':
    main()

