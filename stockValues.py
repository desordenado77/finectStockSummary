import json
import requests
import datetime
from datetime import timedelta
from datetime import datetime
import sys
import os

class bcolors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    
timeDelta = timedelta(days=7)

path = "./"
if sys.platform == "linux2":
    path = "/storage/emulated/0/qpython/scripts/"

with open(path + 'stocks.json') as data_file:    
    data = json.load(data_file)
historyPath = path + "stockHistory/"
if not os.path.exists(historyPath):
    os.makedirs(historyPath)
    
templateText = "{0:20}|{1:12}|{2:12}|{3:12}" 
print templateText.format("Name", " Paid", " Value", " Difference")
line = "-------------------------------------------------------------" 
print line
template = "{0:20}|{1:12.2f}|{2:12.2f}|{3:12.2f}" 
templatePerc = "{0:20}|{1:12.2f}|{2:12.2f}|{3:11.2f}%" 
paidTotal = 0
valueTotal = 0
diffTotal = 0
for elem in data['stocks']:
    url = elem['url']

#    myUrl = url + "?startDate=" + str(timeBefore.year) + "-" + str(timeBefore.month) + "-" + str(timeBefore.day) +"&endDate=" + str(timeNow.year) + "-" + str(timeNow.month) + "-" + str(timeNow.day)

    try:
        values = []
        timeNow = datetime.now()

        while values == [] and (datetime.now()-timeNow)<timedelta(days=45):
            timeBefore = timeNow - timeDelta
        
            myUrl = url + "?startDate=" + str(timeBefore.year) + "-" + str(timeBefore.month) + "-" + str(timeBefore.day) +"&endDate=" + str(timeNow.year) + "-" + str(timeNow.month) + "-" + str(timeNow.day)
            response = requests.get(myUrl)
            response.raise_for_status()

            values = response.json()
            timeNow = timeBefore

        if values != []:
            datetime_value = datetime.strptime("1977-01-01", '%Y-%m-%d')
            theValue = 0


            for value in response.json():
                new_datetime_value = datetime.strptime(value['date'], '%Y-%m-%d')
                new_value = value['value']
                if new_datetime_value > datetime_value:
                    datetime_value = new_datetime_value
                    theValue = new_value

            currentInvestmentValue = float(theValue) * elem['titles']
            gain = float(theValue) * elem['titles'] - elem['paid']
            stockPaidPrice = (elem['paid']/elem['titles'])
            gainPerc = (gain*100)/elem['paid']
            
            color = bcolors.RED
            if gain > 0 :
                color = bcolors.GREEN
                
            print color + template.format(elem['stock'], elem['paid'], currentInvestmentValue, gain)
            print color + templatePerc.format(datetime_value.strftime("%Y-%m-%d"), stockPaidPrice, float(theValue), gainPerc)
            
            paidTotal = paidTotal + elem['paid']
            valueTotal = valueTotal + float(theValue) * elem['titles']
            diffTotal = diffTotal + float(theValue) * elem['titles'] - elem['paid']
            
            print bcolors.ENDC + line
            
            with open(historyPath + elem['stock'].replace(" ", "_")+".csv",'ab') as file:
                file.write(datetime_value.strftime("%Y-%m-%d") + ","+theValue+'\n')
        else :
            color = bcolors.YELLOW
            print color + elem['stock']
            print color + "Unable to retrieve values"
            print bcolors.ENDC + line

    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)

color = bcolors.RED
if diffTotal > 0 :
    color = bcolors.GREEN
print color + template.format("TOTAL:", paidTotal, valueTotal, diffTotal)
templateSummary = "{0:46}|{1:11.2f}%" 
print templateSummary.format("      ",float((diffTotal*100)/paidTotal)) + bcolors.ENDC

