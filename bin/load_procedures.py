#!/usr/bin/env python3

import os

from func import config, db, model

path = config.config['path']

def main():
    with open(os.path.join(path,'data','init','true_proc.txt'),"r") as f:
        for line in f.readlines():
            line = line.strip().replace("'","")
            lsplit = line.split('\t')
            print("lsplit:", lsplit[0], lsplit[1])

            db.session.execute("insert into true_procedure (hcpc_code, name) values ('%s','%s') on conflict (hcpc_code) do update set name = '%s'" % 
                    ( 
                       lsplit[0], lsplit[1], lsplit[1]
                    ))
            db.session.commit()
   


if __name__ == '__main__':
    main()

