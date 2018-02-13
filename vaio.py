#!/usr/bin/env python

import re
import requests
from bs4 import BeautifulSoup
from lxml import html
import json
#import pprint

class vaio:

    url_model_home = "https://esupport.sony.com/US/p/model-home.pl"
    url_driver_landing = "https://esupport.sony.com/p/homefeed-swu.pl"
    url_eula = "https://esupport.sony.com/US/p/swu-download.pl"
    url_base = "https://esupport.sony.com"

    def __init__(self, model):
        self.model = str(model)
              
        # Form instance primary URLs
        driver_landing = vaio.url_driver_landing + "?mdl=" + self.model + "&template_id=1&region_id=1"
        model_home = vaio.url_model_home + "?mdl=" + self.model + "&template_id=1&region_id=1&tab=download#/downloadTab"

        self.model_home = model_home
        self.driver_landing = driver_landing
        self.url_base = vaio.url_base

        soup_driver_landing = self.parse_page(self.driver_landing, allow_redirects=False)
        soup_model_home = self.parse_page(self.model_home, allow_redirects=False)
        
        # Flat file list for the model of all OSes. Some files are shared across OSes but wont be repeated
        filelist = []
        self.filelist = filelist

        if self.status != requests.codes.ok:
            print self.status
            print "Unable to scrape this model:", self.model
            
            # Cannnot proceed with parsing anything since the pages are inaccessible.
            return False
        
        self.soup_driver_landing = soup_driver_landing
        self.soup_model_home = soup_model_home
        
        # Gather up all of the metadata for this model
        self.main()
        
        # Dump gathered info to files
        self.write_json()

    def main(self):
        
        model_summary = {'model': self.model}
        
        self.model_summary = model_summary
        
        # parses model_home
        self.other_names()
        self.model_summary['other_names'] = self.other_mdl_names
        
        # parses driver_landing
        self.supported_os()
        self.model_summary['os_ids'] = self.operating_systems
        
        # parses model_home
        self.model_image_url()
        self.model_summary['image'] = self.image
        
        # parses driver_landing
        self.model_summary['drivers'] = {}
        for os in self.operating_systems:
            drivers = self.parse_drivers(os)
            self.model_summary['drivers'][os] = drivers
        
        metadata = self.model_summary
        self.metadata = metadata
        #pprint.pprint(self.complete)
            
        return self.metadata

    def write_json(self):
        if self.metadata:
            filename = re.sub('[\\/ ]', '_', self.model)
            try:
                with open('./metadata/' + str(filename) + '.json', 'ab') as fh:
                    json.dump(self.metadata, indent=3, fp=fh)
            except:
                print "Error opening json file"
                return False
        if self.filelist:
            try:
                fd = open('./filelist.txt', 'ab')
                for fileurl in self.filelist:
                    print>>fd, fileurl
            except:
                print "Error appending to the file download list"
                    
        
    def clean(self, text):
        '''Remove from a unicode string excess white space, exotic symbol characters, and prefixed "UPDATE " marks. Return the cleaned string back'''
        try:
            text = re.sub('\s+', ' ', text).strip()
            text = re.sub('[^\w \-/\.,:]', '', text)
            text = re.sub('^UPDATE ', '', text)
        except:
            print "Failed to regex clean text:", text
            return
        try:
            text = str(text)
        except:
            print "Failed to convert unicode to python ascii string", text
            return
            
        return text
        
    def parse_page(self, url, params=None, allow_redirects=True):
        '''Input a URL with suffixed query string or an optional parameter dictionary. Returns a parsable bs4 object.'''
        req = requests.get(url, params=params, allow_redirects=allow_redirects)
        status = req.status_code
        self.status = status

        if status == requests.codes.ok:
            try:
                soup = BeautifulSoup(req.text, "lxml")
                return soup
            except:
                print "Failed to scrape or soupify page:", req.url
        else:
            print "Error accessing page! Got:", status, "from", url
            
            return False

    def other_names(self):
        '''Parse all other names for the model from its support home landing page and return it as a list.'''
        soup = self.soup_model_home
       
        other_mdl_names = soup.find('p', {'class': 'removeComma'})
        self.other_mdl_names = other_mdl_names
        try:
            self.other_mdl_names = self.other_mdl_names.text.split(': ')[1:]
            self.other_mdl_names = filter(None, str(self.other_mdl_names[-1]).split(", "))
            
            return self.other_mdl_names
        except:
            print "Failed to parse the other model names:", self.model_home
            
            return False

    def supported_os(self):
        '''Parse the drivers list page for the operating systems with driver support on this model and return a list.'''

        soup = self.soup_driver_landing
        self.operating_systems = []
        try:
            for os in soup.find('select', {'name': 'SelectOS'}).find_all('option'):
                os = self.clean(os['value'])
                if (os != 'Change Operating System') and (os != '0'):
                    self.operating_systems.append(os)
        except:
            print "Malformed list while searching for supported OS"
            return

        return self.operating_systems   

    def model_image_url(self):
        '''Find a jpg source url for a model image thumbnail on the model support home landing page'''
        soup = self.soup_model_home
        image = ''
        self.image = image
        try:
            self.image = soup.find('style', {'type': 'text/css'})
            self.image = self.image.text
            self.image = re.search(r'url\(\'(/.*)\'\)', self.image)
            self.image = self.url_base + str(self.image.groups()[0])
            
            return self.image
            
        except: 
            print "No image found:", self.model_home

    def locate_file(self, url):
        #self.params = {'mdl': self.model, 'upd_id': id, 'os_group_id': os, 'ULA': 'YES'}
        soup = self.parse_page(url + "&ULA=YES")
        download_url = soup.find('a', {'class': 'submit_button'})
        self.download_url = download_url
        try:
            self.download_url = self.download_url['href']
            
            return self.download_url
        except:
            print "Failed to discover driver download with parameters:", self.params
            
            return 'error'

    def download(self, url):
        # https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
        return local_filename

    def os_lookup(self, os):
        '''Get Sony OS ID number for a given OS string'''        
        os_list = {
            'windows 7 64-bit':      6,
            'windows 7':           'x',
            'windows vista 64-bit': 10,
            'windows vista':        10,
            'windows xp 64-bit':   'x',
            'windows xp':           13,
            'windows 2000':          4,
            'windows me:':          21,
            'windows 98/98se':       8,
            'windows 98se':          8,
            'windows 98':            8,
            'windows 95':          'x',
            'windows 3.11':        'x'
        }
        os = os.lower()    

        try:
            self.os_id = str(os_list[os]);
            return self.os_id
        except:
            print "Additional OS not found:", os

    def parse_drivers(self, os=None):
        '''For an OS of the model, parse the driver landing page for the metadata.
        Parse the EULA link for the driver file ID, which can be used to query for a direct file download url
        Dictionary keys: title, info, eulaurl, id, date, version, size
        '''
        
        if os:
            self.soup_driver_landing = self.parse_page(self.driver_landing + "&SelectOS=" + os)
        soup = self.soup_driver_landing
        device_drivers = soup.find_all('div', {'class': 'comp_swu_list'})
        driver_list = []
        self.driver_list = driver_list
        
        try:
            for driver in device_drivers:
                meta = {}
                # Search a soup object for the metadata of each driver
                listing = driver.find('span', {'class': 'filedesc_item'})
                try:
                    meta['eulaurl'] = vaio.url_eula + listing.a['href'].strip()
                    meta['title'] = self.clean(listing.a.text)
                    info = driver.find('span', {'class': 'update_description'})
                    meta['info'] = self.clean(info.text)
                    id = meta['eulaurl']
                    if not os:
                        os = re.search(r'os_group_id=([0-9]+)', id)
                        try:
                            os = str(os.groups()[0])
                        except:
                            print "Failed to parse current OS page from driver download url string:", meta['eulaurl']
                    id = re.search(r'&upd_id=([0-9]+)&?', id)
                    try:
                        id = str(id.groups()[0])
                        meta['id'] = id
                    except:
                        print "Failed to parse driver file ID from url string:", meta['eulaurl']
                        meta['id'] = "error"
                    # Get version, date, size of driver file. Presumptuous string parsing
                    try:
                        for subitem in driver.find_all('span', {'class': 'filedate'}):
                            subitem = re.sub('\t+', '', subitem.text)
                            subitem = filter(None, str(subitem).split('\n'))
                            label = subitem[0].lower().split(' ')[-1]
                            value = subitem[-1]
                            meta[label] = value
                    except:
                        print "Could not parse version, date, size. Probably too presumptuous with the soup page text."
                        meta['version'] = 'error'
                        meta['date'] = 'error'
                        meta['size'] = 'error'
                    try:
                        fileurl = self.locate_file(meta['eulaurl'])
                        meta['filepath'] = fileurl
                        # Some software works across multiple OSes and shares the same file download
                        if fileurl not in self.filelist:
                            self.filelist.append(fileurl)
                        meta['file'] = fileurl.split("/")[-1]
                    except:
                        print "Could not find a file for driver", meta['title'], meta['eulaurl']
                        meta['filepath'] = 'error'
                        meta['file'] = 'error'
                            
                except:
                    print "Failed to find children of filedesc_item. Cannot parse this driver item at:", self.driver_landing
                # One item complete in the file list
                driver_list.append(meta)   
        except:
            print "Failed to find any children of comp_swu_list on this page. Cannot parse drivers:", self.model
            return
        
        # List of driver dictionaries for one OS of one model

        return driver_list
