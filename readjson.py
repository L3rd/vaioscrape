#!/usr/bin/env python

import sys
import re
import json
import pprint


try:
    model = sys.argv[1]
except:
    print "\n"
    print "\tError. Input a model number. Usage:"
    print "\t\t./readjson.py \'VGN-S660\'\n"
    exit(1)

try:
    with open('./' + model + '.json', 'r') as fh:
        data = json.loads(fh.read())
except:
    modelmod = re.sub('[/]', '_', model)
    print "\tError opening model:", model, "\n\tTrying different symbols for the json file:", modelmod
    try:
        with open('./' + modelmod + '.json', 'r') as fh:
            data = json.loads(fh.read())
    except:
        print "\tError finding model. Was it captured yet? Are file permissions correct?\n"
        exit(1)

pprint.pprint(json.dumps(data, indent=5))