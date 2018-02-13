#!/usr/bin/env python

import sys
from subprocess import call
import pprint
import re
from vaio import vaio


def download(url):
    call(["screen", "-dm", "wget", "-a", "./vaiodownload.log", "-t", "5", "-c", "-nc", "-nv", "-P", "./drivers/", url])

try:
    model = sys.argv[1]
    # model = "PCG-Z505LS"
except:
    print "\n"
    print "\tError. Input a model number. Usage:"
    print "\t\t./one.py \'VGN-S660\'\n"
    exit(1)
try:
    print "Scraping... please wait..."
    laptop = vaio(model)
    #pprint.pprint(laptop.metadata)
    print "Now downloading driver files..."
    for url in laptop.filelist:
        print url
        download(url)
    print "Done sending parallel download requests to screen instances. Files may not be finished downloading yet."
except:
    "Error downloading files"
    exit(1)