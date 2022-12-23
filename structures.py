import json
import requests
from urllib.request import urlopen
from json import dumps

for community in range (1,102):
    url = f"https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}"

    # store the response of URL
    response = urlopen(url)
    # storing the JSON response 
    # from url in data
    data_json = json.loads(response.read())
    # print the json response
    #print(data_json
    lands = data_json['lands']
    for l in lands:
        if(l['buildingsAllowed'] == 1 and l['building'] != None):
            #print(l['id'])
            #print (l['building'])
            print(f"Land Id: {l['id']} , Type: {l['building']['type']} , Cost: {l['building']['fee']} $WOOL")