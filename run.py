#!/usr/bin/env python

import json
from subprocess import call
from vaio import vaio
import vaiomodels
import time


def download(url):
    call(["screen", "-dm", "wget", "-a", "./vaiodownload.log", "-t", "5", "-c", "-nc", "-nv", "-P", "./drivers/", url])

def firehose(pclist):
    for model in pclist:
        count = 0
        pc = vaio(model)
        pcdrivers = pc.filelist
        for url in pcdrivers:
        # comment out download(url) to just collect a list of files and the jsons.
            download(url)
            count += 1
        print "Sent", count, "simultaneous download requests to screen and wget. Now sleeping for a bit before moving to next model."
        # If this number is too crazy for your system and network then do 'sudo pkill screen' to stop them all
        time.sleep(20)
    
print "Collecting Vaio models..."
laptops = vaiomodels.laptops
desktops = vaiomodels.desktops
print "Got", len(laptops), "laptops and", len(desktops), "desktops"
firehose(laptops)
firehose(desktops)
print "Some how that all finished without incident and all Sony Vaio drivers have been scraped"
# Should anything mess up, use shell scripts and wget on filelist.txt to have better resuming resources.