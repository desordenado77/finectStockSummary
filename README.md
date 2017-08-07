# finectStockSummary

This is a very simple script that I use to gather the current status of my investments. I use the data from http://www.finect.com which is not the most up to date place, but happens to have all spanish indices and the investments funds I am invested in (which did not seem to be easy to get in other more up to date pages). 

The amount that has been invested and the URL to get the current value is in the json file. The URL for each index was found by reverse engineer the finect webpage. The display is very crude, but it is enough for me for now. I optimized it to be visible on my android phone using qpython. The existing json file does not represent my current investments, it is just dummy values.