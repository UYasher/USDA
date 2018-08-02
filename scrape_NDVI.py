import urllib.request
import re
import time
import pathlib

# find start time
start_time = time.time()

# set URL
url = 'https://gimms.gsfc.nasa.gov/MODIS/std/GMOD09Q1/tif/NDVI/'

#connect to a URL
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Referer': 'https://cssspritegenerator.com',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}
years_website = urllib.request.urlopen(urllib.request.Request(url, data=None, headers=hdr))

#read html code
years_html = years_website.read().decode('utf-8')

#use re.findall to get all the links
year_links = re.findall('"20..\/"', years_html)
print('Years: ' + str(year_links))

# repeat the above process three layers deep in order to download all data

for year_link in year_links:
    year_link = year_link.replace('"', '')
    print('latest year: ' + url+year_link)
    days_website = urllib.request.urlopen(urllib.request.Request(url+year_link, data=None, headers=hdr))
    days_html = days_website.read().decode('utf-8')
    days_links = re.findall('"\d\d\d\/"', days_html)

    for days_link in days_links:
        days_link = days_link.replace('"', '')
        print("latest day:" + url+year_link+days_link)
        data_website = urllib.request.urlopen(urllib.request.Request(url+year_link+days_link, data=None, headers=hdr))
        data_html = data_website.read().decode('utf-8')
        data_links = re.findall('("GMOD..............08d.latlon.x[0][8-9]y0[56].....NDVI.tif.gz"|"GMOD..............08d.latlon.x[1][0-2]y0[56].....NDVI.tif.gz")', data_html)
        print('data_links: ' + str(data_links))
        for data_link in data_links:
            data_link = data_link.replace('"', '')
            print('latest link:' + url+year_link+days_link+data_link)
            file_name = data_link.split('/')[0]
            print('file name:' + file_name)
            
            # write data to file (if file not present).
            if not pathlib.Path(file_name).exists():
                data = urllib.request.urlopen(urllib.request.Request(url+year_link+days_link+data_link, data=None, headers=hdr))
                with open(file_name, "wb+") as f:
                    f.write(data.read())

print("Donwload Complete.")
print("Total time: " + time.time() - start_time)
