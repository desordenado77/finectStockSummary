import json
import requests
import datetime
from datetime import timedelta
from datetime import datetime
import sys

timeDelta = timedelta(days=7)
timeNow = datetime.now()
timeBefore = timeNow - timeDelta

path = "./"
if sys.platform == "linux4":
    path = "/storage/emulated/0/qpython/scripts/"

with open(path + 'stocks.json') as data_file:    
    data = json.load(data_file)

templateText = "{0:20}|{1:12}|{2:12}|{3:12}" 
print templateText.format("Name", "Paid", "Value", "Difference")
line = "-------------------------------------------------------------" 
print line
template = "{0:20}|{1:12.2f}|{2:12.2f}|{3:12.2f}" 
templatePerc = "{0:20}|{1:12.2f}|{2:12.2f}|{3:12.2f}%" 
paidTotal = 0
valueTotal = 0
diffTotal = 0
for elem in data['stocks']:
    url = elem['url']

    myUrl = url + "?startDate=" + str(timeBefore.year) + "-" + str(timeBefore.month) + "-" + str(timeBefore.day) +"&endDate=" + str(timeNow.year) + "-" + str(timeNow.month) + "-" + str(timeNow.day)

    try:
        response = requests.get(myUrl)
        response.raise_for_status()

        values = response.json()

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

        print template.format(elem['stock'], elem['paid'], currentInvestmentValue, gain)
        print templatePerc.format(datetime_value.strftime("%Y-%m-%d"), stockPaidPrice, float(theValue), gainPerc)

        paidTotal = paidTotal + elem['paid']
        valueTotal = valueTotal + float(theValue) * elem['titles']
        diffTotal = diffTotal + float(theValue) * elem['titles'] - elem['paid']
        
        print line

    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)

print template.format("TOTAL:", paidTotal, valueTotal, diffTotal)
templateSummary = "{0:46}|{1:12.2f}%" 
print templateSummary.format("      ",float((diffTotal*100)/paidTotal))

