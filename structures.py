import json
import requests
from urllib.request import urlopen
from json import dumps

denCount=0
denCost = 0

barnCount =0
barnCost =0

bathhouseCount = 0
bathhouseCost = 0

bathhousePeakCount =0
bathhousePeakCost = 0

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
            if l['building']['type'] == "DEN":
                denCount +=1
                denCost += l['building']['fee']
            elif l['building']['type'] == "BATHHOUSE":
                if community != 101:
                    bathhouseCount +=1
                    bathhouseCost += l['building']['fee']
                else:
                    bathhousePeakCount +=1
                    bathhousePeakCost += l['building']['fee']                
            elif l['building']['type'] == "BARN":
                barnCount +=1
                barnCost += l['building']['fee']
            else:
                print("oops")

print(f"BARNS:{barnCount}  DENS:{denCount}  SHEEP BATH HOUSE COUNT:{bathhouseCount}   PEAK BATH HOUSE COUNT:{bathhousePeakCount}  TOTAL BATHHOUSES: {bathhousePeakCount+bathhouseCount}")

print(f"BARN AVG COST:{barnCost/barnCount}")
print(f"DEN AVG COST:{denCost/denCount}")
print(f'BATHHOUSE AVG COST:{bathhouseCost/bathhouseCount}')
print(f'BATHHOUSEPEAK AVG COST:{bathhousePeakCost/bathhousePeakCount}')