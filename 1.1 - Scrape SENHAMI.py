"""
Scrape weather data from SENHAMI
Last modified: 14/11/2018
author: SSB
run time: around 40h (highly sensitive to internet download speed)
"""

#----------------------------------------------------------------------------------------------------------------
#Preamble
import os
import shutil
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen

os.chdir("/Volumes/Documents/")
start_time = time.time()
Stations_txt = open("in/SENHAMI/Stations.txt",  'r')
stations = []
for row in Stations_txt:
    station_code = row.split("\n")[0]
    stations.append(station_code)
Stations_txt.close()
print("a")
def reset_folders():
    key = input("Type CONFIRM to continue...")
    print(key)
    if key == "CONFIRM":
        for yy in range(1960, 2019):
            shutil.rmtree("in/SENHAMI/html daily/{0}".format(yy))
            os.mkdir("in/SENHAMI/html daily/{0}".format(yy))
    else:
        print("aborting reset")
reset_folders() #uncomment to reset folders

#1. Monthly Data and Characteristics for Each Station
senhami_sub_url = "http://www.senamhi.gob.pe/include_mapas/_dat_esta_tipo02.php/?estaciones="
for i in range(0, 1000):
    station = stations[i]

    #1.1 Get daily data on monthly batches
    for yy in range(1990, 1991):
        for mm in range(1,13):
            if mm < 10:
                date = "{0}0{1}".format(yy, mm)
            else:
                date = "{0}{1}".format(yy, mm)
            senhami_url = senhami_sub_url + "{0}&tipo=CON&CBOFiltro={1}&t_e=M&e=csv".format(station, date)
            senhami_bs  = BeautifulSoup(urlopen(senhami_url), "lxml")
            senhami_str = str(senhami_bs)
            html = open("in/SENHAMI/html daily/{0}/station_{1}_date_{2}_{3}.html".format(yy,station,yy,mm), "w", encoding = "latin1")
            html.write(senhami_str)
            if size < 3500:
                os.remove(file_path_original)
            html.close()
        print("done scrapping data on station {0}/1000  (batch 1) over the period {1}".format(i+1,yy))

    #1.2 Station Characteristics
    senhami_url = senhami_sub_url + "{0}".format(station)
    senhami_bs  = BeautifulSoup(urlopen(senhami_url), "lxml")
    senhami_str = str(senhami_bs)
    html = open("in/SENHAMI/station characteristics/station_{0}.html".format(station), "w", encoding = "utf-8")
    html.write(senhami_str)
    html.close()
    print("done scrapping data on station {0}/1000  (batch 1)".format(i+1))

ellapsed = time.time() - start_time
print("This takes {0}s".format(ellapsed))
