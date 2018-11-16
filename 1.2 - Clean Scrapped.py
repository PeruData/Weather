"""
HTML data from SENHAMI is translated to dta
Last modified: 16/11/2018
author: SSB
run time: almost 10h (but only 15s for part 2)
"""

#----------------------------------------------------------------------------------------------------------------------------------
#Preamble
import copy
import glob
import pandas as pd
import os
import re
import shutil
import time
from bs4 import BeautifulSoup

os.chdir("/Volumes/Backup Mac/GRADE/Climate and Education/00_Data")

#Define function to replace non-ASCII characters
def to_ascii(str):
    original    = ['á','é','í','ó','ú','Á','É','Í','Ó','Ú','°','º','ñ','Ñ','ü','¿','“','”','–','"',]
    modified    = ['a','e','i','o','u','A','E','I','O','U','','','ni','Ni','u','','','','','']
    for i in range(len(original)):
        str         = str.replace(original[i],modified[i])
    return str

#1. Weather Data
start_time = time.time()
for yy in range (1990,2017):
    df_master =  pd.DataFrame(columns=['station', 'date', 'TemperaturaMax_c_', 'TemperaturaMin_c_', 'Temperatura_BulboSeco_c_07', 'Temperatura_BulboSeco_c_13', 'Temperatura_BulboSeco_c_19', 'Temperatura_BulboHumedo_c_07', 'Temperatura_BulboHumedo_c_13', 'Temperatura_BulboHumedo_c_19', 'Precipitacion_mm_07', 'Precipitacion_mm_19', 'DirecciondelViento_13h', 'VelocidaddelViento_13h_m_s'])
    yy_file    = 'in/SENHAMI/html daily clean/{0}/'.format(yy)
    for file in os.listdir(yy_file):
        html_path = yy_file + file
        html      = open(html_path, 'r', encoding = 'latin-1')
        bs        = BeautifulSoup(html, 'lxml')
        table     = bs.find('table')
        n_cols    = 0
        n_rows    = 0
        #we will create a pandas dataframe based on the dimensions of a table
        #first get the dimensions of the table with this loop:
        for row in table.findAll('tr'):
            col_tags = row.findAll(['td', 'th'])
            if len(col_tags) > 0:
                n_rows += 1
                if len(col_tags) > n_cols:
                        n_cols = len(col_tags)
        df = pd.DataFrame(index = range(0, n_rows), columns = range(0, n_cols))

        # Create list to store rowspan values
        skip_index = [0 for i in range(0, n_cols)]

        #extract data cell by cell
        row_counter = 0
        for row in table.findAll('tr'):
            #skip the row if it's blank
            if len(row.findAll(['td', 'th'])) == 0:
                next
            else:
            # Get all cells containing data in this row
                columns = row.find_all(['td', 'th'])
                col_dim = []
                row_dim = []
                col_dim_counter = -1
                row_dim_counter = -1
                col_counter = -1
                this_skip_index = copy.deepcopy(skip_index)  #'deepcopy' is not just assignment, it creates a second identical object
                for col in columns:
                    # Determine cell dimensions
                    #vertical dimension
                    #if column span is 1, 'colspan' property will not be found
                    colspan = col.get('colspan')
                    if colspan is None:
                        col_dim.append(1)
                    else:
                        col_dim.append(int(colspan))
                    col_dim_counter += 1
                    #horizontal dimension
                    rowspan = col.get('rowspan')
                    if rowspan is None:
                        row_dim.append(1)
                    else:
                        row_dim.append(int(rowspan))
                    row_dim_counter += 1
                    # Adjust column counter
                    if col_counter == -1:
                        col_counter = 0
                    else:
                        col_counter = col_counter + col_dim[col_dim_counter - 1]
                    while skip_index[col_counter] > 0:
                        col_counter += 1
                    # Get cell contents
                    cell_data = col.get_text()
                    cell_data = to_ascii(cell_data)
                    # Insert this data into cell (iat[x,y] allows us to access element at position [x,y])
                    df.iat[row_counter, col_counter] = cell_data
                    # Record column skipping index
                    if row_dim[row_dim_counter] > 1:
                        this_skip_index[col_counter] = row_dim[row_dim_counter]
                # Adjust row counter
                row_counter += 1
                # Adjust column skipping index
                skip_index = [i - 1 if i > 0 else i for i in this_skip_index]

        #Export to Stata
        #Debugging one exception: rename 'Dia/mes/año' to 'date'
        df.iat[0, 0] = 'date'
        #Fixing names of variables:
        df = df.fillna('')
        for i in range(0, n_cols):
            if df.iat[0,i] == '':
                df.iat[0,i] = df.iat[0,i - 1] #this fixes leftovers from merged column names
        for col in range(0, n_cols):
            df.iat[0, col] = df.iat[0, col] + df.iat[1, col]
        df = df.drop([1])
        varnames = df.iloc[0]
        df = df[1:]
        for i,varname in enumerate(varnames):
            new_varname = varname
            new_varname = new_varname.replace(' ','_')
            new_varname = new_varname.replace('(mm)','mm')
            new_varname = new_varname.replace('(c)','c_')
            new_varname = new_varname.replace('(m/s)','m_s')
            new_varname = new_varname.replace('7_','7')
            varnames[i] = new_varname
        df.columns = varnames
        df['station'] = file.split('_date')[0].split('station_')[1]
        df_master = df_master.append(df, ignore_index=True, sort = False)
    df_master.to_stata('in/SENHAMI/to_stata/appended_{00}.dta'.format(yy), encoding = 'latin1')
    print('DONE with {0}'.format(yy))
ellapsed = time.time() - start_time
print('This takes {0}s'.format(ellapsed))

#2. Station Characteristics
start_time = time.time()
df_master =  pd.DataFrame(columns=['station', 'name', 'type', 'dep', 'prov', 'dist', 'latitud', 'longitud', 'altitude'])
characteristics_file = 'in/SENHAMI/station characteristics/'
def sexagesimal_to_decimal(str):
    degree_int = float(str.split("°")[0])
    minute_int = float(str.split("°")[1].split("'")[0])/60
    second_int = float(str.split("'")[1].split("''")[0])/3600
    coordinate_decimals = -(degree_int + minute_int + second_int)
    return coordinate_decimals

c = 1
for file in os.listdir(characteristics_file):
    if file[-5:] != '.html':
        continue
    html_path = characteristics_file + file
    html      = open(html_path, 'r', encoding = 'utf-8')
    bs        = BeautifulSoup(html, 'lxml')
    html_path
    station   = html_path.split("station_")[1].split(".html")[0]
    name      = bs.find('div', text = re.compile('Estación')).get_text().split(':')[1].split(',')[0].strip().replace(' ', '_')
    type      = to_ascii(bs.find('div', text = re.compile('Estación')).get_text().split(' Tipo ')[1].replace(' - ', '_').strip())
    dep       = to_ascii(bs.find('div', text = re.compile('Departamento')).find_next('td').get_text())
    prov      = to_ascii(bs.find('div', text = re.compile('Provincia')).find_next('td').get_text())
    dist      = to_ascii(bs.find('div', text = re.compile('Distrito')).find_next('td').get_text())
    try:
        latitude  = sexagesimal_to_decimal(bs.find('div', text = re.compile('Latitud')).find_next('td').get_text())
        longitude = sexagesimal_to_decimal(bs.find('div', text = re.compile('Longitud')).find_next('td').get_text())
    except:
        latitude  = -999
        longitude = -999
    altitude  = bs.find('div', text = re.compile('Altitud')).find_next('td').get_text()
    new_row = [station, name, type, dep , prov, dist, latitude, longitude, altitude]
    df_master.loc[c] = new_row
    c +=1
df_master.to_stata('in/SENHAMI/to_stata/station characteristics.dta', encoding = 'latin-1')
ellapsed = time.time() - start_time
print('This takes {0}s'.format(ellapsed))
