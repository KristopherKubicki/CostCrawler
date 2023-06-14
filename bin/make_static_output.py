#!/usr/bin/env python3

import os
import time
import requests

from func import config, db, model

path = config.config['path']

def main():
      with open(os.path.join(path,'data','init','zone.txt'),"r") as f:
        for line in f.readlines():
            line = line.replace("'","")
            lsplit = line.strip().split('\t')
            if lsplit[0] == 'Zip':
                continue

            #r = requests.get("http://beta.waymed.com:5000/zone/%s/tsv" % lsplit[0])
            r = requests.get("http://beta.waymed.com:5000/zone/%s/json" % lsplit[0])
            if r and r.status_code == 200:
                print("done", lsplit[0], len(r.text.split('\n')))
                # todo: make sure its json
                with open('/tmp/cache/zones/%s.json' % lsplit[0],"w") as w:
                    w.write(r.text)
            else:
                print("problem:", lsplit[0], r.status_code)
            time.sleep(0.1)
            continue


if __name__ == '__main__':
    main()

