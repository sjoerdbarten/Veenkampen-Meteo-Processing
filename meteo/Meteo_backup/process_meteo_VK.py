import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import os
import shutil
import pysftp as sftp
import make_graphs_def
import resample_funcs # resampling functions for ten-minute and hourly files
import VK_tools # management of the columns
from glob import glob
import subprocess

#
# Define directories


# raw data location (from loggernet)
RawdataDir = 'C:/Veenkampen/Data/'

#
# archiving of raw data 
#

archive_rawdatadir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/raw_data/'   # on W-drive
loc_archive_rawdatadir = 'D:/veenkampen_archive/raw_data/'   # on local external hard disk

#
# Storage of prcessed data
#

# on local harddrive of L0153962

DataDir = 'C:/veenkampen_data/data_exp/'

# archving the processed data

archive_datadir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/veenkampen_data/'   # on W-drive
loc_archive_datadir = 'D:/veenkampen_archive/veenkampen_data/'    # on local external hard disk

#
# directory for placing biomet (metgeg.txt) file used by Eddypro
#

flux_dir = 'C:/Veenkampen_data/flux_exp/'


#
# *** Definition of the variables and their positions in the different files ***
# the function get_table is in the python routine VK_tool.get_table.py
# output are two python dicts:
# 1) north_list_dict containing all data that comes in from North logger
# 2) south_list_dic containing all data that comes from the south logger
# the keys of the dict contain the names of the variable (see get_table in VK_tools.py for an explanation)
# each item in the dict contains a tuple of five integers:
# zero'th integer identifies wether the variable is logged by the north or the south logger (1= North, 2 =South)
# first integer identifies the column number of the variable in the input file (=file from loggernet)
# second integer identifies which processing needs to be done for the 10_minute, hourly and daily avaerages (see VK_tool.py for explanantion)
# third integer identifies the column number of the variable in the 10_minute, hourly and daily file
# fourth integer identief the column number of the variable in the 1_minute file (North and South combined)
 
north_list_dict,south_list_dict = VK_tools.get_table()

#
# concatenate the two dicts from South and North loggers
#

north_south_combined = {**north_list_dict,**south_list_dict}

#
# Here the processing starts
# *** Determine the dates of the last ten-minute interval ***

tm = datetime.utcnow()  # find current time (in UTC)

# round time to last finisched 10-minute interval

tm = tm - timedelta(minutes=tm.minute % 10, seconds=tm.second, microseconds=tm.microsecond)


# set startdate and enddate

startdate = tm+timedelta(days=-1, minutes=1)
stopdate = tm

# *** Read data of North side ***


#
# here, the reading of the data from the North logger starts
#

filename = RawdataDir+'VeenkampenNorth_stats' # define prefix of file names

#
# the reading of the data happens in a function get_data24h that is part of
# a python file called VK_tools.py. In this routine two files are being read:
# RawdataDir+'VeenkampenNorth_stats.dat', which is loggernet data of the current month
# RawdataDir+'VeenkampenNorth_stats_prevmonth.dat', which is the loggernet data of the previous month
# Output of the function is all loggernet data from the last 24 hours (one-minute_data)
#

last_10minute_north_from_loggernet = VK_tools.get_data24h(filename, startdate, stopdate)

#
# a copy is made of the data collected from loggernet that can be processed

last_10minute_north = last_10minute_north_from_loggernet
last_10minute_north = last_10minute_north.replace(-999., np.nan)    # replace -999 by nan for calculations

#
# copy the loggernet file to the archive and the local archive
#

shutil.copy(filename+'.dat',archive_rawdatadir+'VeenkampenN/') # W-drive
# 13-06-2023 KvdD below directory does not excist ??
shutil.copy(filename+'.dat',loc_archive_rawdatadir+'VeenkampenN/') # local archive

# adjust wind speeds: sonics sometimes on error when u > 35m/s=126km/h, put value to nan (later to -999.)

s1 = north_list_dict['windspeed 10 m sonic'][1] # sonic 10 meter 
s2 = north_list_dict['windspeed 10 m sonic  max'][1] # windspeed 10 m sonic  max
s3 = north_list_dict['windspeed 2m'][1]  # windspeed 2m 
s4 = north_list_dict['windspeed 2m max'][1]  # windspeed 2m max

#
# concatenate the sonic wind speed
#

ws_sonic = pd.concat([last_10minute_north[s1], last_10minute_north[s2], last_10minute_north[s3],
                      last_10minute_north[s4]], axis=1, keys=[s1, s2, s3, s4])

# adjust wind speed when u < 35 m/s

ws_sonic = ws_sonic.where(ws_sonic <= 35., np.nan)

#
# update variables sonic wind speeds
#

for key in [s1, s2, s3, s4]:
    last_10minute_north[key] = ws_sonic[key]

# snow height correction

s1 = north_list_dict['snow height'][1]
last_10minute_north[s1] = (1. - last_10minute_north[s1]) * 100.  # WHY TO SNOWHEIGHT?!!!!!

# pressure correction

s1 = north_list_dict['Pressure'][1]
last_10minute_north[s1] = last_10minute_north[s1] - 0.125       # CORRECT?!!!!!!!!!!!


# *** Read statistics of South side ***


# here, the reading of the data from the South logger starts

filename = RawdataDir+'VeenkampenSouth_stats'

#
# the reading of the data happens in a function get_data24h that is part of
# a python file called VK_tools.py. In this routine two files are being read:
# RawdataDir+'VeenkampenSouth_stats.dat', which is loggernet data of the current month
# RawdataDir+'VeenkampenSouth_stats_prevmonth.dat', which is the loggernet data of the previous month
# Output of the function is all loggernet data from the last 24 hours (one-minute_data)
#


last_10minute_south_from_loggernet = VK_tools.get_data24h(filename, startdate, stopdate)
last_10minute_south = last_10minute_south_from_loggernet
last_10minute_south = last_10minute_south.replace(-999., np.nan)    # replace -999 by nan for calculations

#
# copy the loggenert file to the archive and the local archive
#

shutil.copy(filename+'.dat',archive_rawdatadir+'VeenkampenS/')
# 13-06-2023 KvdD below directory does not excist ??
shutil.copy(filename+'.dat',loc_archive_rawdatadir+'VeenkampenS/')

# correct sunshine values

s1 = south_list_dict['Sunshine'][1]
sh = last_10minute_south[s1]
sh = sh.where(sh >= 33, 0.)

#
# calculate sunshine duration to seconds values
#

last_10minute_south[s1] = sh/1000.*60.

# adjust Tgrass 50 cm

s1 = south_list_dict['Tgras   50cm'][1]
last_10minute_south[s1] = np.nan

# recalculate QNET from Qs_in - Qs_out + Ql_in - Ql_out

s1 = south_list_dict['Qglb in'][1]
s2 = south_list_dict['Qglb out'][1]
s3 = south_list_dict['QL in'][1]
s4 = south_list_dict['QL out'][1]
snet = south_list_dict['Qnet'][1]

last_10minute_south[snet] = last_10minute_south[s1] - last_10minute_south[s2] \
                                        + last_10minute_south[s3] - last_10minute_south[s4]



# *** Make 1-minute values, and 10-minute and hourly averages of North and South combined***

dti = pd.date_range(start=startdate,end=stopdate,freq='T')

#
# define a pandas dataframe for one-minute output values
#

max_colnr = max([value[4] for key,value in north_south_combined.items()])

out_1minute = pd.DataFrame(np.nan, index=dti, columns=range(max_colnr+1))

#
# define a pandas dataframe for ten-minute output values
#

max_colnr = max([value[3] for key,value in north_south_combined.items()])

out_10minute = pd.DataFrame(index=out_1minute.resample('10T', label='right', closed='right').mean().index,
                            columns=range(max_colnr+1))

#
# define a pandas dataframe for hourly output values
# has six less columns because extra columns rainfall measurements are not in hourly data
#

out_hour = pd.DataFrame(index=out_1minute.resample('1H', label='right', closed='right').mean().index,
                            columns=range(max_colnr-6+1))

#
# loop through all variables in North and South loggernet variables
#



for key,jj in north_south_combined.items():

#
# jj[0] is whether it is North or South Logger
# jj[1] is the position of the variable in the input dataframes (north and south loggers)
# jj[2] is the calculation that needs to be done for 10-minute, hourly and daily files
# jj[3] is the column number of the variable in 10-minute,hourly and the daiy file
#


    if jj[0] == 1:
        last_10minute = last_10minute_north[jj[1]].reindex(dti)
    elif jj[0] == 2:
        last_10minute = last_10minute_south[jj[1]].reindex(dti)
    else:
        print('non-existent datalogger')


    if jj[2] != 10: # variables for which nothing needs to be done

        out_1minute[jj[4]] = last_10minute


    if jj[2] == 1: # variables for which the ten-minute, hourly and daily contain a mean variable
        
        s1 = jj[3] # column number of mean
        varin = last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        
        if jj[3] < 83: # no need of extra parameters of rainfall measurement
           varin = last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.mean)
           out_hour[s1] = varin 
  

    elif jj[2] == 2: # variables for which the ten-minute, hourly and daily contain a mean,max variable
        
        s1 = jj[3] # column number of mean
        s2 = jj[3]+1 # column number of max

        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s2] = varin 
        
        if jj[3] < 83: # no need of extra parameters of rainfall measurement
           varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.mean)
           out_hour[s1] = varin 
           varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.max)
           out_hour[s2] = varin 

    elif jj[2] == 3: # variables for which the ten-minute, hourly and daily contain a mean,max,min variable
        
        s1 = jj[3] # column number of mean
        s2 = jj[3]+1 # column number of min
        s3 = jj[3]+2 # column number of max

        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.min)
        out_10minute[s2] = varin
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s3] = varin 
 
        if jj[3] < 83:
            varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.mean)
            out_hour[s1] = varin 
            varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.min)
            out_hour[s2] = varin 
            varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.max)
            out_hour[s3] = varin 
  
   
    elif jj[2] == 4: # variables for which the ten-minute, hourly and daily contain a summed variable
        s1 = jj[3] # column number of sum
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.sum)
        if jj[0] == 2:
            varin=varin/60.     # sunshine in minutes            
        out_10minute[s1] = varin 
        
        if jj[3] < 83:
           varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.sum)
           if jj[0] == 2:
              varin=varin/60.     # sunshine in minutes
              varin=varin*10./60. # conform KNMI standard (.1 hour sunshine per hour)
           out_hour[s1] = varin 


    elif jj[2] == 5: # variables for which the angles need to be resampled
        s1 = jj[3] # column number of mean of angles
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.calc_angles)
        out_10minute[s1] = varin 

        if jj[3] < 83:
          varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.calc_angles)
          out_hour[s1] = varin
          
    elif jj[2] == 6: # variables for which the ten-minute, hourly and daily contain a positive mean variable
        
        s1 = jj[3] # column number of positive mean
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.pos_mean)
        out_10minute[s1] = varin 

        if jj[3] < 83:
           varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.pos_mean)
           out_hour[s1] = varin 
    
    elif jj[2] == 7: # variables for which the ten-minute, hourly and daily contain a max variable
        
        s1 = jj[3] # column number of max
        varin=last_10minute.resample('10T', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s1] = varin 
        if jj[3] < 83:
          varin=last_10minute.resample('1H', label='right', closed='right').apply(resample_funcs.max)
          out_hour[s1] = varin 
    else:
        print('not defined: ', jj,jj[2])


#
# add date, time as first and second column of one-minute output
#
out_1minute[0] = out_1minute.index.strftime('%Y-%m-%d') # date
out_1minute[1] = out_1minute.index.strftime('%H:%M') # time

#
# add date, time as first and second column of ten-minute output
#
out_10minute[0] = out_10minute.index.strftime('%Y-%m-%d') # date
out_10minute[1] = out_10minute.index.strftime('%H:%M') # time

#
# add date, time as first and second column of hourly output
#

out_hour[0] = out_hour.index.strftime('%Y-%m-%d') # date
out_hour[1] = out_hour.index.strftime('%H') # time


#
# rewrite last hour of hourly output as 24 hour of previous day
#

index24= out_hour.index[out_hour[1] == '00'].to_list() 
out_hour.loc[index24[0],0] = (tm+timedelta(days=-1)).strftime('%Y-%m-%d')
out_hour.loc[index24[0],1] = '24'

# Replace NaN by -999.

last_10minute_north = last_10minute_north.replace(np.nan, -999.)
last_10minute_south = last_10minute_south.replace(np.nan, -999.)
out_1minute = out_1minute.replace(np.nan, -999.)
out_10minute = out_10minute.replace(np.nan, -999.)
out_hour = out_hour.replace(np.nan,-999.)

# *** Append file to compute fluxes ***
#
#   desired sensors (column numbers)
#   TA =  7         RH = 17          PA = 31      SWIN = 18       SWOUT = 19
#   LWIN = 20       LWOUT = 21       SWDIFF = 23
# With more options, like in Excel:

metgeg_vars = out_10minute[[8, 18, 32, 37, 29, 19, 20, 21, 22, 24]].iloc[-1].round(2).tolist()
metgeg_vars_str = []
for kk in range(len(metgeg_vars)):
    if kk == 3:
        val = str(int(np.round(metgeg_vars[kk]))) + ' '     # to match output format of metgeg.txt
    else:
        val = '{:.2f}'.format(metgeg_vars[kk]) + ' '        # to match output format of metgeg.txt
    metgeg_vars_str.append(val)
date_metgeg = [out_10minute[0][-1], out_10minute[1][-1][:2], out_10minute[1][-1][-2:]]
line_metgeg = [','.join(date_metgeg + metgeg_vars_str) + '\n']
# load metgeg.txt   # can be simplified when directories finalised: use 'a' for append instead of read and write!

#
# reading of current metgeg.txt files used by Eddypro
#

rfile = open(flux_dir + 'metgeg.txt', 'r')
all_lines = rfile.readlines()
rfile.close()

# Write variables to file

del all_lines[2] # delete first line to keep the numbr of line in the metgeg.txt file

lines2write = all_lines + line_metgeg
out_metgeg = flux_dir + 'metgeg.txt'
file2write = open(out_metgeg, 'w')
file2write.writelines(lines2write)
file2write.close()


# 
# copy metgeg.txt file to archive and local archive
#

shutil.copy(out_metgeg,archive_datadir+'flux/') # w-drive
shutil.copy(out_metgeg,loc_archive_datadir+'flux/') # local archive


# *** Save North and South data to currentn.txt and currents.txt ***

f_north = open(DataDir+'currentn.txt.','w')
for idx,rows in last_10minute_north_from_loggernet.iterrows():
   date_str = idx.strftime('"%Y-%m-%d %H:%M:%S"')
   out_row = ','.join([date_str]+[str(row).rstrip('0').rstrip('.') for row in rows])
   f_north.write(out_row+'\n')
f_north.close()
#last_10minute_north.to_csv(DataDir + 'currentn.txt', index=True, header=False)

# copy currentn.txt to archive

shutil.copy(DataDir+'currentn.txt',archive_datadir) # w-drive
shutil.copy(DataDir+'currentn.txt',loc_archive_datadir) # local archive

f_south = open(DataDir+'currents.txt.','w')
for idx,rows in last_10minute_south_from_loggernet.iterrows():
   date_str = idx.strftime('"%Y-%m-%d %H:%M:%S"')
   out_row = ','.join([date_str]+[str(row).rstrip('0').rstrip('.') for row in rows])
   f_south.write(out_row+'\n')
f_south.close()

# copy currentn.txt to archive

shutil.copy(DataDir+'currents.txt',archive_datadir) # w-drive
shutil.copy(DataDir+'currents.txt',loc_archive_datadir) # local archive

#last_10minute_south.to_csv(DataDir + 'currents.txt', index=True, header=False)

# *** Write C_current.txt ***

f_Cur = open(DataDir+'C_current.txt.','w')
for idx,rows in out_1minute.iterrows():
    out_row = ['"'+rows[0]+'"',rows[1]]
    qnet_id = north_south_combined['Qnet'][4]
    pres_id = north_south_combined['Pressure'][4]
   
    for iter in range(2,len(rows)):
       if iter == qnet_id: # Qnet
         out = '% .1f'% rows[iter]
         out_row.append(out.rstrip('0'))
       elif iter == pres_id: # pressure
         out_row.append(str(rows[iter]))
       elif iter == 54: # empty cell
          out_row.append('')
       else: # all other variables
         out_row.append(VK_tools.formatting(rows[iter]))

    out_row_str = ','.join(out_row)
    f_Cur.write(out_row_str+'\n')
f_Cur.close()

# copy C_current.txt to archive

shutil.copy(DataDir+'C_current.txt',archive_datadir) # w-drive
shutil.copy(DataDir+'C_current.txt',loc_archive_datadir) # local archive

#out_1minute.to_csv(DataDir + 'C_current.txt', index=False, header=False)


# 
# make 10min_current.txt
#

f_tenminute = open(DataDir + '10min_current.txt','w')
for idx,rows in out_10minute.iterrows():
   out_row = ['"'+rows[0]+'"',rows[1]]  
   for iter in range(2,len(rows)):
      
      wd_10 = north_south_combined['wind direction 10 m sonic'][3]
      wd_2 = north_south_combined['wind 2m direction'][3]
     
      if (iter == wd_10) or (iter == wd_2):
          out = '%.f' % rows[iter]
          out_row.append(out+' ')

      elif (iter == 81): # empth cell
           out_row.append('')
      else:
           out = '%.2f' % rows[iter] # other variables
           out_row.append(out+' ')
      
   out_row_str = ','.join(out_row)
   f_tenminute.write(out_row_str+'\n')
f_tenminute.close()

#
# copy 10inute_current.txt to archive
#
shutil.copy(DataDir+'10min_current.txt',archive_datadir) # w-drive
shutil.copy(DataDir+'10min_current.txt',loc_archive_datadir) # local archive


#
# make hourly file
#
    
f_hour = open(DataDir + 'uurdata.txt','w')
for idx,rows in out_hour.iterrows():
    out_row = [rows[0],rows[1]]  
    for iter in range(2,len(rows)-2):
       out = '%.3f' % rows[iter]
       out_row.append(out)
    for iter in range(81,89): out_row.append('') # create empty cells as last columns
    out_row_str = ','.join(out_row)
    f_hour.write(out_row_str+'\n')
f_hour.close()   

#
# copy uurdata.txt to archive
#
 
shutil.copy(DataDir+'uurdata.txt',archive_datadir)
shutil.copy(DataDir+'uurdata.txt',loc_archive_datadir)

#
# make all graphs for the website
#

make_graphs_def.make_plots(False,startdate)


subprocess.run(['c:/veenkampen/meteo/copygraphs_tometwurnl.bat','cur'])

# 
# send C_current.txt, currentn.txt,currents.txt to website veenkampen.nl/data
#

subprocess.run(['c:/veenkampen/meteo/copyfiles_totransip.bat'])

#cnopts = sftp.CnOpts()
#cnopts.hostkeys = None          

#try:
#  srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
#  srv.cwd('/www/')
#  srv.cwd("data")
#  srv.put(DataDir+'C_current.txt')
#  srv.put(DataDir+'currents.txt')
#  srv.put(DataDir+'currentn.txt')
#  srv.put(DataDir+'10min_current.txt')
#  srv.put(DataDir+'uurdata.txt')
#  srv.put(flux+dir+'metgeg.txt')
#  srv.close()
#except:
#  print('no connection with transip files')

# 
# send all graphs to website veenkampen.nl/graphs/cur
#

#graphs_dir = 'C:/veenkampen/meteo/graphs/cur/'     
#files_all = glob(graphs_dir+'*png')
#try:
#  srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
#  srv.cwd('/www/graphs/cur/')
#  for file in files_all: srv.put(file)
#  srv.close()
#except:
#  print('no connection with transip plots')
