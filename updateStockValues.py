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

try:
    r = requests.get(project_url+stock_values_file_name)
    try:
        shutil.move(path+stock_values_file_name, path+old_stock_values_file_name)
    except Exception,e: 
        print str(e)        
        
    with open(path + stock_values_file_name, "w") as data_file:    
        data_file.write(r.text)
        
#    r = requests.get(project_url+updater_file_name)
    
#    shutil.move(path+updater_file_name, path+old_updater_file_name)
#    with open(path + updater_file_name) as data_file:    
#        data_file.write(r.text)        
except Exception,e: 
    print "Error found. Unable to update"
    print str(e)