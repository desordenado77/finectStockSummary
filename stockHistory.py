import json
import sys
import os
import shutil

# ap comes from https://github.com/mfouesneau/asciiplot
# I am using c54956d0be3a44d82e03465924e3a44f17dc4ac5
import ap, numpy as np
import datetime



def drawGraph(x, y=None, marker=None, shape=(75, 15), draw_axes=True,
         newline='\n', plot_slope=False, x_margin=0.05,
         y_margin=0.1, plot_labels=True, xlim=None, ylim=None):
    flags = {'shape': shape,
             'draw_axes': draw_axes,
             'newline': newline,
             'marker': marker,
             'plot_slope': plot_slope,
             'margins': (x_margin, y_margin),
             'plot_labels': plot_labels }

    p = ap.AFigure(**flags)

    print p.plot(x, y, marker=marker, plot_slope=plot_slope, xlim=xlim, ylim=ylim).encode('utf-8')



path = "./"
if sys.platform == "linux4":
    path = "/storage/emulated/0/qpython/scripts/"

with open(path + 'stocks.json') as data_file:    
    data = json.load(data_file)
    
historyPath = path + "stockHistory/"

# epoch = datetime.datetime(1970,1,1)
timeNow = datetime.datetime.now()

for elem in data['stocks']:
    x=[]
    y=[]
    # remove duplicated
    prevLine = ""
    fileName = historyPath + elem['stock'].replace(" ", "_")+".csv"
    origFileName = fileName+".orig"
    shutil.move(fileName, origFileName)
    with open(origFileName,'rb') as fileRead:
        with open(fileName,'wb') as fileWrite:
            for line in fileRead:
                if line != prevLine:
                    fileWrite.write(line)
                    prevLine = line
                    xstr = line.split(",")[0]
                    ystr = line.split(",")[1]


                    datetime_object = datetime.datetime.strptime(xstr, '%Y-%m-%d')
                    # comparing to epoch
                    # cts = (datetime_object-epoch).total_seconds()
                    cts = ((datetime_object-timeNow).total_seconds())/(60*60*24)
                    
                    # print int(cts)
                    x.append(int(cts))
                    y.append(float(ystr))
                    
            minx = min(x)
            # does not seem to handle negative values right
            x[:] = [a - minx for a in x]
            miny = min(y)
            maxy = max(y)

            miny = miny - (maxy-miny)/10
            maxy = maxy + (maxy-miny)/10
            print "\n\n\n"
            print elem['stock']+ "  --------   Paid per stock: " + str(elem['paid']/elem['titles'])

            drawGraph(x, y, marker='x', xlim=[min(x),max(x)], ylim=[miny, maxy])
            
    os.remove(origFileName)
