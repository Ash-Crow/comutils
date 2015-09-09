#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gets all pictures from Wiki Loves Africa 2014 and figures out some statistics

import requests
import json
import csv
from collections import Counter

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen



def commons_api_query(query, gcmcontinue = ''):
    """
    Queries the Wikimedia Commons API and returns the result
    """
    query_url = 'https://commons.wikimedia.org/w/api.php?' + query 

    if gcmcontinue:
        query_url += '&gcmcontinue=' + gcmcontinue

    response = urlopen(query_url)
    encoding = 'utf-8'

    result = json.loads(response.read().decode(encoding))

    return result


query_params = "action=query&prop=imageinfo&format=json&iiprop=size|mime|mediatype|metadata&rawcontinue="
query_params += "&generator=categorymembers&gcmtitle=Category%3AImages_from_Wiki_Loves_Africa_2014&gcmnamespace=6&gcmtype=file&gcmlimit=500"

query_result = commons_api_query(query_params)

#print query_result
gcmcontinue = query_result['query-continue']['categorymembers']['gcmcontinue']

img_sizes = []
img_widths = []
img_heights = []

cameras = {}

while gcmcontinue != '':
    pages =  query_result['query']['pages']

    for p, v in pages.items():
        imageinfo = v['imageinfo'][0]
        img_sizes.append(imageinfo['size'])

        img_widths.append(imageinfo['width'])
        img_heights.append(imageinfo['height'])

        metadata = imageinfo['metadata']
        make = ''
        model = ''
        if metadata:
            for m in metadata:

                if m['name'] == 'Make':
                    make = m['value']
                if m['name'] == 'Model':
                    model = m['value']

            if make and model:
                if make not in cameras:
                    cameras[make] = []
                cameras[make].append(model)

    query_result = commons_api_query(query_params, gcmcontinue)
    if 'query-continue' in query_result:
        gcmcontinue = query_result['query-continue']['categorymembers']['gcmcontinue']
    else:
        gcmcontinue = ''

min_img_size = min(img_sizes)
max_img_size = max(img_sizes)
avg_img_size = sum(img_sizes)/float(len(img_sizes))
print "Image sizes (min/max/avg): {} / {} / {}".format(min_img_size, max_img_size, avg_img_size)

min_img_width = min(img_widths)
max_img_width = max(img_widths)
avg_img_width = sum(img_widths)/float(len(img_widths))
print "Image widths (min/max/avg): {} / {} / {}".format(min_img_width, max_img_width, avg_img_width)

min_img_height = min(img_heights)
max_img_height = max(img_heights)
avg_img_height = sum(img_heights)/float(len(img_heights))
print "Image heights (min/max/avg): {} / {} / {}".format(min_img_height, max_img_height, avg_img_height)

cameras_count = {}
for make, models in cameras.items():
    cameras_count[make] = Counter()
    for model in models:
        cameras_count[make][model] += 1

with open('cameras.csv', 'wb') as csv_file:
    wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    wr.writerow(['Make', 'Model', 'Count', 'Type'])
    for make, models in cameras_count.items():
        for model, count in models.items():
            wr.writerow([make, model, count, ''])
    print "Camera counts written in cameras.csv."
