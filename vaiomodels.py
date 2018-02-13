#!/usr/bin/env python


import requests
import json
from bs4 import BeautifulSoup


url_laptops = "https://esupport.sony.com/perl/select-xml.pl?template=EN&region_id=1&mdltype_id=24"
url_desktops = "https://esupport.sony.com/perl/select-xml.pl?template=EN&region_id=1&mdltype_id=1"

def write_json(pylist, filename):
    try:
        with open(str(filename) + '.json', 'w') as fh:
            json.dump(pylist, indent=3, fp=fh)
    except:
        print "Error opening json file"
        return False

def get_models(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'lxml')
    models = []
    for item in soup.find_all('modelname'):
        models.append(str(item.text.strip()))

    return models

laptops = get_models(url_laptops)
desktops = get_models(url_desktops)

write_json(laptops, "laptops")
write_json(desktops, "desktops")