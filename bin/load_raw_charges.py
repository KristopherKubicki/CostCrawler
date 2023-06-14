#!/usr/bin/env python3

# depricated

import os

from func import config, db, model, numbers

path = config.config['path']


def main():
    with open(os.path.join(path,'data','init','raw_charges.txt'),"r") as f:
        (loaded,counted) = (0,0)
        for line in f.readlines():
            line = line.strip().replace("'","")
            lsplit = line.split('\t')
            lsplit[0] = lsplit[0].strip()
            counted += 1
            if not lsplit[0].isdigit():
                print("skipping facility:", lsplit[0])
                print("lsplit:", lsplit[0], lsplit[4], lsplit[5], lsplit[6])
                continue

            lsplit[5] = lsplit[5].strip()
            lsplit[4] = lsplit[4].strip()

            lsplit[6] = lsplit[6].strip()
            lsplit[6] = lsplit[6].replace(" ","")
            lsplit[6] = lsplit[6].replace("$","")
            lsplit[6] = lsplit[6].replace(",","")
            if not numbers.ismoney(lsplit[6]):
                print("skipping charge: '", lsplit[6], "'")
                print("lsplit:", lsplit[0], lsplit[4], lsplit[5], lsplit[6])
                continue

            db.session.execute("insert into raw_procedure (bill_id, description) values ('%s','%s') on conflict do nothing" % 
                    (lsplit[4], lsplit[5]) 
                    )
            db.session.commit()

            # get the raw_procedure_id
            ret = (db.session
                    .query(model.RawProcedure)
                    .filter(model.RawProcedure.bill_id == lsplit[4])
                    .filter(model.RawProcedure.description == lsplit[5])
                    .first())
            if not ret:
                print("warning missing charge!", lsplit[4], lsplit[5])
                continue

            try:
                db.session.execute("insert into raw_charge (facility_id, raw_procedure_id, charge, start_time) values ('%d','%d','%.2f', null) on conflict on constraint facility_proc_charge do update set charge = '%.2f'" % 
                    ( 
                       int(lsplit[0]), ret.raw_procedure_id, float(lsplit[6]), float(lsplit[6])
                    ))
                db.session.execute("update raw_procedure set raw_charge_count = raw_charge_count + 1 where raw_procedure_id = '%d'" % ret.raw_procedure_id)
                loaded += 1

            except Exception as e:
                db.session.rollback()
                continue
            db.session.commit()
            print("loaded:", loaded, counted)
   


if __name__ == '__main__':
    main()

