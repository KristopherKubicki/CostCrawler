
import sqlalchemy as sa
import re
import requests
import datetime
import json
#import googlesearch
from uszipcode import Zipcode, SearchEngine
import bs4
import time

from tldextract import extract
from urllib3.exceptions import InsecureRequestWarning

from func import config, db, model


def get_all_facilities():
    return db.session.query(model.Facility).all()


def get_facility_by_id(facility_id):
    assert facility_id

    return db.session.query(model.Facility).filter(model.Facility.facility_id == facility_id).first()


def scrape_facility(facility):

    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


    nearby_zips = []
    population = 0
    if facility.latitude and facility.longitude:
        search = SearchEngine(simple_zipcode=False)
        lret = search.by_coordinates(facility.latitude, facility.longitude, radius=30, returns=500, sort_by=Zipcode.population, ascending=False)
        if len(lret) > 0:
            for lzip in lret:
                population += lzip.population
                nearby_zips.append(lzip.zipcode)
    facility.population = population
    
    search_string = facility.name
    if facility.address:
        search_string += ' ' + facility.address
    if facility.postal_code and facility.postal_code not in search_string:
        search_string += ' ' + facility.postal_code

    facility.scrape_time = datetime.datetime.utcnow()

    # TODO: get social

    lids = []
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=%s&input=%s&inputtype=textquery&locationbias=point:%.5f,%.5f' % (config.config['gv_key'], search_string, facility.latitude, facility.longitude)
    print("url:", url)
    headers = {'Accept': 'application/json'}
    r = requests.post(url, headers=headers)
    if r and r.json():
        results = r.json()
        if results.get('candidates'):
            for lret in results['candidates']:
                if lret.get('place_id'):
                    print("DETECTED:", lret)
                    lids.append(lret['place_id'])

    results = None
    for lid in lids:
        url = 'https://maps.googleapis.com/maps/api/place/details/json?key=%s&place_id=%s' % (config.config['gv_key'], lid)
        print("url:", url)
        headers = {'Accept': 'application/json'}
        r = requests.post(url, headers=headers)
        if r and r.json():
            results = r.json()
            facility.scrape_json = results
            # TODO: check for hospital in types
            #  if no hospital, skip

            if results.get('result'):
                if results['result'].get('name'):
                    facility.display_name = results['result']['name']
                if results['result'].get('international_phone_number'):
                    facility.phone = results['result']['international_phone_number']
                if results['result'].get('website'):
                    facility.homepage = results['result']['website']
                    print("website:", facility.homepage)

            if facility.homepage:
                break
    if population and results:
       results['population'] = population
    if nearby_zips and results:
       results['nearby_zips'] = nearby_zips

    db.session.commit()

    if facility.domain and results:
       page_black_list = ['.pdf']
       print("found domain:", facility.domain)
       potential_urls = []
       search_terms = ['price list', 'price transparency', 'chargemaster']
       headers = {"Ocp-Apim-Subscription-Key": config.config['ms_key']}
       search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
       for st in search_terms:
           search_term = 'site:%s %s' % (facility.domain, st)
           params = {"q": search_term, "textDecorations": False, "textFormat": "HTML"}
           response = requests.get(search_url, headers=headers, params=params)
           if not response and not response.json and not response.json.get('webPages'):
               print("no response!")
               continue
           results['price_search_json'] = response.json()
           if response.json().get('webPages') and response.json()['webPages'].get('value'): 
               for lref in response.json()['webPages']['value']: 
                   lurl = lref['url']
                   tsd, td, tsu = extract(lurl)
                   ldomain = td + '.' + tsu
                   if ldomain == facility.domain and lurl not in potential_urls:
                       skipper = False
                       for bl in page_black_list:
                           if bl in lurl.lower():
                               skipper = True
                       if not skipper:
                           #print("pricepages:", lurl)
                           potential_urls.append(lurl)

       results['pricepages'] = potential_urls
       facility.scrape_json = results
       db.session.commit()

       price_white_list = ['price','txt','xls']
       price_links = []
       for lurl in potential_urls:
           tsd, td, tsu = extract(lurl)
           full_domain = tsd + '.' + td + '.' + tsu

           lret = requests.get(lurl, verify=False)
           if not lret and not lret.text:
               continue
           for pwl in price_white_list:
               if pwl in lurl and lurl not in price_links:
                   price_links.append(lurl)
           try:
             soup = bs4.BeautifulSoup(str(lret.text), "lxml")
             for alink in soup.find_all('a'):
               if not alink:
                   continue
               try:
                 link = alink.get('href')
                 if not link:
                     continue

                 if link[0:4].lower() != 'http':
                     if link[0] == '/':
                         link = full_domain + link
                     else:
                         link = full_domain + '/' + link
                      
                 tsd, td, tsu = extract(link)
                 ldomain = td + '.' + tsu
                 if ldomain == facility.domain and link not in potential_urls and link not in price_links:
                   llink = link.lower()
                   for pwl in price_white_list:
                        if pwl in llink:
                            print("hit:", link)
                            price_links.append(link)
               except Exception as e:
                   print("warning:", e)
                   pass
           except Exception as e:
               print("bs4 exception!", lurl, e)

       results['pricelists'] = price_links
       facility.scrape_json = results
       db.session.commit()


    return
