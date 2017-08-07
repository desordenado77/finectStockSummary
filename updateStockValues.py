import requests
import sys
import shutil


project_url = "https://raw.githubusercontent.com/desordenado77/finectStockSummary/master/"
stock_values_file_name = "stockValues.py"
old_stock_values_file_name = "stockValuesOld.py"

updater_file_name = "updateStockValues.py"
old_updater_file_name = "updateStockValuesOld.py"

path = "./"
if sys.platform == "linux4":
    path = "/storage/emulated/0/qpython/scripts/"

fileList = ["stockValues.py", "updateStockValues.py" ]  

for element in fileList:    
    try:
        print "attempting to update " + element
        
        r = requests.get(project_url+element)
        try:
            shutil.move(path+element, path+"old_"+element)
        except Exception,e: 
            print str(e)        
            
        with open(path + element, "w") as data_file:    
            data_file.write(r.text)
            
        print element + " Updated"
    except Exception,e: 
        print "Error found. Unable to update " + element
        print str(e)