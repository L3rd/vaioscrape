# vaioscrape
Capture from esupport.sony.com their metadata and driver installation files, as they're ending support in March.
Scraping is done with requests & beautifulsoup. Downloads are calls to wget from python.

## Python Module Dependencies
  * bs4
  * requests
  * lxml
  * json

## vaio.py
Per model python class for scraping the driver files and metadata; such as title, description, size, os, etc.
Appends unique entries per model to ./filelist.txt
Writes <modelname>.json to ./metadata/
## vaiomodels.py
Scrapes for a complete model list of desktop and laptop Vaio products
Writes to ./desktops.json and ./laptops.json
## readjson.py
Example for reading back the json data into python
Can be called from the shell with '<modelname>' to print its metadata to STDOUT read from ./metadata/<modelname>.json
Or tinker with the code to do stuff with reloaded python dictionaries
Note that '/' symbols in model name get converted to underscore '_' but either works for the script in the shell arg input
## run.py
Example grab-all script using the above mentioned scripts along with wget called from python. Logic is very dumb and you may end up with 30+ simultaneous downloads.
## one.py
Example option to input one model in as a shell arg and download its meta data and drivers. Probably a better option to use than run.py, for there are better ways to do parallel downloads. It also will build upon filelist.txt as you use it.
onedl.png

## Pathway to the firehose of data:
Run at your own risk! No guarantees of best practices, best conventions, or safety to your system and network resources.
Dev & testing was done in a debian based distro (ubuntu or raspbian would work).

## Setup & Go
```
sudo apt install -y python python-pip virtualenv wget screen
cd ~/my_massive_storage_space
git clone https://github.com/jwhittaker/vaioscrape.git && cd vaioscrape
virtualenv env
source env/bin/activate
pip install bs4 requests lxml
./run.py
```

In another window monitor downloads with: `tail -f ./vaiodownload.log`
