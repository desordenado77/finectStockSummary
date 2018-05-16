#qpy:2
#qpy:webapp:stockHistory
#qpy://localhost:8080/stockHistory

from bottle import Bottle, run
from bottle import static_file
from bottle import response
import shutil

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading

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

path = "./"

app = Bottle()
host = '127.0.0.1'

stocks_json = []
paidVal_json = []
data = []
stockValuesArrayJson = []
totalsJson = {}
statusJson = {}

def getGoogleValues(url):
    response = requests.get(url)
    response.raise_for_status()
    strResponse = response.text

    if strResponse.startswith("\n// ") :
        strResponse = strResponse[3:]
        jsonResp = json.loads(strResponse)
        return (jsonResp[0]["l"]).replace(',','')

    return 0

def getAvantageValues(url):
    response = requests.get(url)
    response.raise_for_status()
    strResponse = response.text

    jsonResp = json.loads(strResponse)

    jsonTimeSeries = jsonResp["Time Series (Daily)"]
    maxdatetime = datetime.strptime("1977-01-01", '%Y-%m-%d')
    value = 0
    for elem in jsonTimeSeries:
        elemdatetime = datetime.strptime(elem, '%Y-%m-%d')
        if elemdatetime > maxdatetime :
            maxdatetime = elemdatetime
            value = jsonTimeSeries[elem]["4. close"]

    return [ value, maxdatetime ]



def getStockValues():    
    timeDelta = timedelta(days=7)

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
    elemCnt = 0
    elements = len(data['stocks'])
    datetime_now = datetime.now()

    for elem in data['stocks']:
        stockValuesJson = {}
        url = elem['url']
        urlGoogle = ""
        datetime_value = datetime.strptime("1977-01-01", '%Y-%m-%d')
        theValue = 0

        try:
            urlAvantage = elem['urlAvantage']
            [ theValue, datetime_value ] = getAvantageValues(urlAvantage)
        except KeyError as error:
            pass
            
        if theValue == 0 :
            try:
                urlGoogle = elem['urlGoogle']
                theValue = getGoogleValues(urlGoogle)
                datetime_value = datetime_now
            except KeyError as error:
                pass

        statusJson['status'] = str(elemCnt) + " of " + str(elements)

        elemCnt = elemCnt + 1
        
        try:
            if theValue == 0 :
                values = []
                timeNow = datetime_now

                while values == [] and (datetime_now-timeNow)<timedelta(days=45):
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

            if theValue != 0 :
                currentInvestmentValue = float(theValue) * elem['titles']
                gain = float(theValue) * elem['titles'] - elem['paid']
                stockPaidPrice = (elem['paid']/elem['titles'])
                gainPerc = (gain*100)/elem['paid']
                
                color = bcolors.RED
                if gain > 0 :
                    color = bcolors.GREEN
                    
                print color + template.format(elem['stock'], elem['paid'], currentInvestmentValue, gain)
                print color + templatePerc.format(datetime_value.strftime("%Y-%m-%d"), stockPaidPrice, float(theValue), gainPerc)
                
                stockValuesJson['stock'] = elem['stock']
                stockValuesJson['paidTotal'] = elem['paid']
                stockValuesJson['investmentValue'] = currentInvestmentValue
                stockValuesJson['gain'] = gain
                stockValuesJson['date'] = datetime_value.strftime("%Y-%m-%d")
                stockValuesJson['paidPerStock'] = stockPaidPrice
                stockValuesJson['currValue'] = float(theValue)
                stockValuesJson['gainPerc'] = gainPerc

                stockValuesArrayJson.append(stockValuesJson)

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
            stockValuesJson['stock'] = elem['stock']
            stockValuesJson['paidTotal'] = elem['paid']
            stockValuesJson['investmentValue'] = 0
            stockValuesJson['gain'] = 0
            stockValuesJson['date'] = "1970-1-1"
            stockValuesJson['paidPerStock'] = 0
            stockValuesJson['currValue'] = 0
            stockValuesJson['gainPerc'] = 0

            stockValuesArrayJson.append(stockValuesJson)

            print(error.response.status_code, error.response.text)

    color = bcolors.RED
    if diffTotal > 0 :
        color = bcolors.GREEN
    print color + template.format("TOTAL:", paidTotal, valueTotal, diffTotal)
    templateSummary = "{0:46}|{1:11.2f}%" 
    print templateSummary.format("      ",float((diffTotal*100)/paidTotal)) + bcolors.ENDC

    totalsJson['paidTotal'] = paidTotal
    totalsJson['valueTotal'] = valueTotal
    totalsJson['gain'] = diffTotal
    totalsJson['gainPerc'] = float((diffTotal*100)/paidTotal)

    for elem in data['stocks']:
        # remove duplicated
        prevLine = ""
        fileName = historyPath + elem['stock'].replace(" ", "_")+".csv"
        origFileName = fileName+".orig"
        shutil.move(fileName, origFileName)
        firstLine = 1
        with open(origFileName,'rb') as fileRead:
            with open(fileName,'wb') as fileWrite:
                for line in fileRead:
                    if firstLine == 1:
                        if line != "Date,Value\n":
                            fileWrite.write("Date,Value\n")
                        firstLine = 0
                    if line != prevLine:
                        fileWrite.write(line)
                        prevLine = line
                
                stocks_json.append("" + elem['stock'].replace(" ", "_"))
                paidVal_json.append(elem['paid']/elem['titles'])

        os.remove(origFileName)

    statusJson['status'] = "Done"

    return


@app.route('/stockHistory')
def stockHistory():
    return static_file("./indexNew.html", root=path)

@app.route('/<filename>')
def js(filename):
    if filename.endswith(".js"):
        print filename
        return static_file(filename, root=path)
    if filename.endswith(".csv"):
        print filename
        return static_file(filename, root=path + 'stockHistory/')

@app.route('/stocks.json')
def stocksjson():
    response.content_type = 'application/json'
    return json.dumps(stocks_json)

@app.route('/paidVal.json')
def paidVal():
    response.content_type = 'application/json'
    return json.dumps(paidVal_json)

@app.route('/stockValuesArray.json')
def stockValuesArrayjson():
    response.content_type = 'application/json'
    return json.dumps(stockValuesArrayJson)

@app.route('/totals.json')
def totalsjson():
    response.content_type = 'application/json'
    return json.dumps(totalsJson)

@app.route('/status.json')
def statusjson():
    response.content_type = 'application/json'
    return json.dumps(statusJson)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith(".html") or self.path.endswith(".js") :
                f = open(path + self.path)

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            if self.path.endswith(".csv") :
                f = open(path + "stockHistory" + sep + self.path)

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)


# dummy call to avoid the following error:
#  ImportError: Failed to import _strptime because the import lockis held by another thread.
# this is as per https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=166912
datetime.strptime("2016", '%Y')

if sys.platform == "linux4":
    path = "/storage/emulated/0/qpython/scripts/"
else :
    host = '0.0.0.0'

with open(path + 'stocks.json') as data_file:    
    data = json.load(data_file)
    
t = threading.Thread(target=getStockValues)
t.start()

run(app, host=host, port=8080)
