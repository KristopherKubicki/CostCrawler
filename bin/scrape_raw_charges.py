import googlesearch
import time

data_file = 'raw_il'  # your input file here 

with open(data_file, "r") as f:
    for line in f.read().splitlines():
        ldomains = []
        lurls = []
        lprices = []
        lsheets = []
        try:
          for j in googlesearch.search(line, lang='en', num=10, stop=10, pause=20):
            ldomain = j.split("//")[-1].split("/")[0].split('?')[0]
            if ldomain in ['www.ahd.com', 'healthcare4ppl.com']:
                continue

            lurls.append(j)
            ldomains.append(ldomain)
            for k in googlesearch.search("site:%s price transparency" % ldomain, lang='en', num=10, stop=10, pause=20):
                if '.pdf' in k or '.doc' in k:
                    continue
                lprices.append(k)
                # Note, this code was lost in 2021 and needs to be recreated.  
                #  TODO: pull down the URL. Look for any tables, test to see if there are charge codes
                #  if so, parse each row into the following format
                #  Facility ID     Facility Name   Date    Source Sheet    Bill ID Description     Charge
                # ex
                #  140174  PRESENCE MERCY MEDICAL CENTER   12/15/2019      https://docs.google.com/spreadsheets/d/1YbLeMdXSDyM_WxLa3WmKc72opaF6ZH3Ott4OVZYuEjs/edit#gid=608674038  61010095        MRI UPR EXTR RT W/O CON $3,237.00
                # sort sheet is not that import and just for your own reference.  

        except Exception as e:
          print("exception:", e)
          pass

