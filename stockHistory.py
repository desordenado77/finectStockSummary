#qpy:2
#qpy:webapp:Hello Qpython
#qpy://localhost:8080/stockHistory

from bottle import Bottle, run
from bottle import static_file

import json
import sys
import os
import shutil

import datetime

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

path = "./"

app = Bottle()

@app.route('/stockHistory')
def stockHistory():
    return static_file("./index.html", root='./')

@app.route('/<filename>')
def js(filename):
    if filename.endswith(".js"):
        print filename
        return static_file(filename, root='./')
    if filename.endswith(".csv"):
        print filename
        return static_file(filename, root='./stockHistory/')

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith(".html") or self.path.endswith(".js") :
                f = open(path + self.path) #self.path has /test.html
#note that this potentially makes every file on your computer readable by the internet

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            if self.path.endswith(".csv") :
                f = open(path + "stockHistory" + sep + self.path) #self.path has /test.html
#note that this potentially makes every file on your computer readable by the internet

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)




if sys.platform == "linux4":
    path = "/storage/emulated/0/qpython/scripts/"

with open(path + 'stocks.json') as data_file:    
    data = json.load(data_file)
    
historyPath = path + "stockHistory/"

# epoch = datetime.datetime(1970,1,1)
timeNow = datetime.datetime.now()

stockHistory_js_line1 = "var stocks = ["
stockHistory_js_line2 = "var paidVal = ["

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
            
            stockHistory_js_line1 = stockHistory_js_line1 + "\"" + elem['stock'].replace(" ", "_") + "\", "
            stockHistory_js_line2 = stockHistory_js_line2 + str(elem['paid']/elem['titles']) + ", "

    os.remove(origFileName)

# remove the las comma
stockHistory_js_line1 = rreplace(stockHistory_js_line1, ',', '', 1)
stockHistory_js_line2 = rreplace(stockHistory_js_line2, ',', '', 1)

with open(path + "stockHistory.js", 'wb') as fileWrite:
    fileWrite.write(stockHistory_js_line1)
    fileWrite.write("];\n")
    fileWrite.write(stockHistory_js_line2)
    fileWrite.write("];\n")


run(app, host='localhost', port=8080)
