import requests
import sys
import shutil

# workaround based on https://github.com/qpython-android/qpython3/issues/61
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMPLEMENTOFDEFAULT"

project_url = "https://raw.githubusercontent.com/desordenado77/finectStockSummary/master/"

path = "./scripts"
if sys.platform == "linux2":
    path = "/storage/emulated/0/qpython/scripts/"

fileList = ["stockValues.py", "stockHistory.py", "updateStockValues.py", "index.html", "myStocks.py", "indexNew.html" ]  

for element in fileList:    
    try:
        print("attempting to update " + element)
        
        r = requests.get(project_url+element)
        try:
            shutil.move(path+element, path+"old_"+element)
        except Exception as e: 
            print(str(e))
            
        with open(path + element, "w") as data_file:    
            data_file.write(r.text)
            
        print(element + " Updated")
    except Exception as e: 
        print(("Error found. Unable to update " + element))
        print(str(e))