import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import os
import shutil
import pysftp as sftp
import make_graphs_def
import resample_funcs
import VK_tools
from dateutil.relativedelta import relativedelta
from glob import glob
import subprocess

pd.set_option("future.no_silent_downcasting", True)

# *** Directories ***
# raw data (from loggernet)

RawdataDir = 'C:/Veenkampen/Data/'

#
# archiving of raw data 
#

archive_rawdatadir = 'W:/ESG\DOW_MAQ/MAQ_Archive/Veenkampen_archive/raw_data/' #w-drive
loc_archive_rawdatadir = 'D:/veenkampen_archive/raw_data/' # local archive

# where to store the data
# local

DataDir = 'C:/veenkampen_data/'

# archive
archive_datadir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/veenkampen_data/' # w-drive
loc_archive_datadir = 'D:/veenkampen_archive/veenkampen_data/' # local archive
 
# *** Definition of the variables and their positions in the different files ***

north_list_dict, south_list_dict = VK_tools.get_table()

#
# concatenate the two dicts from South and North loggers
#


north_south_combined = {**north_list_dict,**south_list_dict}

# processing starts
# *** Determine the dates of the last ten-minute interval ***

tm_now = datetime.utcnow()
tm = datetime(tm_now.year,tm_now.month,tm_now.day,0,0) # round to 0:00 UTC

startdate = tm+timedelta(days=-1, minutes=1)
stopdate = tm
print(startdate,stopdate)

# here, the reading of the data from the North logger starts

filename = RawdataDir+'VeenkampenNorth_stats'

#
# the reading of the data happens in a function get_data24h that is part of
# a python file called VK_tools.py. In this routine two files are being read:
# RawdataDir+'VeenkampenNorth_stats.dat', which is loggernet data of the current month
# RawdataDir+'VeenkampenNorth_stats_prevmonth.dat', which is the loggernet data of the previous month
# Output of the function is all loggernet data from the last 24 hours (one-minute_data)
#

last_10minute_north_from_loggernet = VK_tools.get_data24h(filename, startdate, stopdate)
last_10minute_north = last_10minute_north_from_loggernet
last_10minute_north = last_10minute_north.replace(-999., np.nan)    # replace -999 by nan for calculations

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

# optimize sunshine values

s1 = south_list_dict['Sunshine'][1]
sh = last_10minute_south[s1]
sh = sh.where(sh >= 33, 0.)

#
# calculate sunshine duration to second values
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

dti = pd.date_range(start=startdate,end=stopdate,freq='min')

max_colnr = max([value[4] for key,value in north_south_combined.items()])

#
# define a pandas dataframe for one-minute output values
#

out_1minute = pd.DataFrame(np.nan, index=dti, columns=range(max_colnr+1))

max_colnr = max([value[3] for key,value in north_south_combined.items()])

#
# define a pandas dataframe for ten-minute output values
#

out_10minute = pd.DataFrame(index=out_1minute.resample('10min', label='right', closed='right').mean().index,
                            columns=range(max_colnr+1))

#
# define a pandas dataframe for hourly and daily output values
#

out_hour = pd.DataFrame(index=out_1minute.resample('1h', label='right', closed='right').mean().index,
                            columns=range(max_colnr-6+1))

out_day = pd.DataFrame(index=out_1minute.resample('1D', label='left', closed='right').mean().index,
                            columns=range(max_colnr-6+1))


#
# processing of the different variables start
#


for key,jj in north_south_combined.items():
    
#
# jj[0] is whether it is North or South Logger
# jj[1] is the position of the variable in the input dataframes (north and South loggers)
# jj[2] is the calculation that needs to be done for 10-minute, hourly and daily files
# jj[3] is the column number of the variable in 10-minute,hourly and the daiy file
# jj[4] is the column number of the variable in the one-minutefile
#

    if jj[0] == 1:
        last_10minute = last_10minute_north[jj[1]].reindex(dti)
    elif jj[0] == 2:
        last_10minute = last_10minute_south[jj[1]].reindex(dti)
    else:
        print('non-existent datalogger')

    if jj[2] != 10:
        out_1minute[jj[4]] = last_10minute

    if jj[2] == 1:
        
        s1 = jj[3]
        varin = last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        
        if jj[3] < 83:
           varin = last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.mean)
           out_hour[s1] = varin 
           varin = last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.mean)
           out_day[s1] = varin 
 

    elif jj[2] == 2:
        
        s1 = jj[3]
        s2 = jj[3]+1
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s2] = varin 
        
        if jj[3] < 83:
           varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.mean)
           out_hour[s1] = varin 
           varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.max)
           out_hour[s2] = varin 
           varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.mean)
           out_day[s1] = varin 
           varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.max)
           out_day[s2] = varin 

    elif jj[2] == 3:
        
        s1 = jj[3]
        s2 = jj[3]+1
        s3 = jj[3]+2
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.mean)
        out_10minute[s1] = varin 
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.min)
        out_10minute[s2] = varin
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s3] = varin 
 
        if jj[3] < 83:
            varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.mean)
            out_hour[s1] = varin 
            varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.min)
            out_hour[s2] = varin 
            varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.max)
            out_hour[s3] = varin 
            varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.mean)
            out_day[s1] = varin 
            varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.min)
            out_day[s2] = varin 
            varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.max)
            out_day[s3] = varin 
  
   
    elif jj[2] == 4:
        s1 = jj[3]
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.sum)
        if jj[0] == 2:
            varin=varin/60.     # sunshine in minutes
        out_10minute[s1] = varin 
        
        if jj[3] < 83:
           varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.sum)
           if jj[0] == 2:
              varin=varin/60.     # sunshine in minutes
              varin=varin*10./60. # conform KNMI standard: sunshine in .1 hour per hour)
           out_hour[s1] = varin 

        if jj[3] < 83:
           varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.sum)
           if jj[0] == 2:
              varin=varin/60.     # sunshine in minutes
           out_day[s1] = varin 


    elif jj[2] == 5:
        s1 = jj[3]
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.calc_angles)
        out_10minute[s1] = varin 

        if jj[3] < 83:
          varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.calc_angles)
          out_hour[s1] = varin
          
          varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.calc_angles)
          out_day[s1] = varin 

    elif jj[2] == 6:
        s1 = jj[3]
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.pos_mean)
        out_10minute[s1] = varin 

        if jj[3] < 83:
           varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.pos_mean)
           out_hour[s1] = varin 

           varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.pos_mean)
           out_day[s1] = varin 
    elif jj[2] == 7:
        s1 = jj[3]
        varin=last_10minute.resample('10min', label='right', closed='right').apply(resample_funcs.max)
        out_10minute[s1] = varin 
        if jj[3] < 83:
          varin=last_10minute.resample('1h', label='right', closed='right').apply(resample_funcs.max)
          out_hour[s1] = varin 

          varin=last_10minute.resample('1D', label='left', closed='right').apply(resample_funcs.max)
          out_day[s1] = varin 

    else:
        print('not defined: ', jj,jj[2])

#
# add date, time as first and second column of one-minute output
#

out_1minute[0] = out_1minute.index.strftime('%Y-%m-%d')
out_1minute[1] = out_1minute.index.strftime('%H:%M')

#
# add date, time as first and second column of ten-minute output
#

out_10minute[0] = out_10minute.index.strftime('%Y-%m-%d')
out_10minute[1] = out_10minute.index.strftime('%H:%M')

#
# add date, time as first and second column of hourly output
#

out_hour[0] = out_hour.index.strftime('%Y-%m-%d')
out_hour[1] = out_hour.index.strftime('%H')

#
# add date, time as first and second column of daily output
#

out_day[0] = out_day.index.strftime('%d-%m-%Y')
out_day[1] = str(out_day.index[0].day)+'.00'

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
out_day = out_day.replace(np.nan,-999.)


# 
# path of datadir
#

path = os.path.join(DataDir,startdate.strftime('%Y/%m/'))
os.makedirs(path,exist_ok=True)

#
# path of archive (w-drive)
#

path_archive = os.path.join(archive_datadir,startdate.strftime('%Y/%m/'))
os.makedirs(path_archive,exist_ok=True)

#
# patch of local archive
#

path_loc_archive = os.path.join(loc_archive_datadir,startdate.strftime('%Y/%m/'))
os.makedirs(path_loc_archive,exist_ok=True)

# save north logger file as daily file
f_north = open(path+'N'+startdate.strftime('%Y%m%d')+'.txt','w')

f_north = open(path+'N'+startdate.strftime('%Y%m%d')+'.txt','w')
for idx,rows in last_10minute_north_from_loggernet.iterrows():
   date_str = idx.strftime('"%Y-%m-%d %H:%M:%S"')
   out_row = ','.join([date_str]+[str(row).rstrip('0').rstrip('.') for row in rows])
   f_north.write(out_row+'\n')
f_north.close()

# copy north logger daily file to archive

shutil.copy(path+'N'+startdate.strftime('%Y%m%d')+'.txt',path_archive) # w-drive
shutil.copy(path+'N'+startdate.strftime('%Y%m%d')+'.txt',path_loc_archive) # local archive


# save south logger file as daily file

f_south = open(path+'S'+startdate.strftime('%Y%m%d')+'.txt','w')
for idx,rows in last_10minute_south_from_loggernet.iterrows():
   date_str = idx.strftime('"%Y-%m-%d %H:%M:%S"')
   out_row = ','.join([date_str]+[str(row).rstrip('0').rstrip('.') for row in rows])
   f_south.write(out_row+'\n')
f_south.close()

# copy south logger daily file to archive

shutil.copy(path+'S'+startdate.strftime('%Y%m%d')+'.txt',path_archive) # w-drive
shutil.copy(path+'S'+startdate.strftime('%Y%m%d')+'.txt',path_loc_archive) # local archive

# *** Write C_current.txt  as daily file***

f_Cur = open(path+'C_'+startdate.strftime('%Y%m%d')+'.txt','w')
for idx,rows in out_1minute.iterrows():
    out_row = ['"'+rows[0]+'"',rows[1]]

    qnet_id = north_south_combined['Qnet'][4]
    pres_id = north_south_combined['Pressure'][4]

    for iter in range(2,len(rows)):
       if iter == qnet_id:
         out = '% .1f'% rows[iter]
         out_row.append(out.rstrip('0'))
       elif iter == pres_id:
         out_row.append(str(rows[iter]))
       elif iter == 54:
          out_row.append('')
       else:
         out_row.append(VK_tools.formatting(rows[iter]))

    out_row_str = ','.join(out_row)
    f_Cur.write(out_row_str+'\n')
f_Cur.close()

# copy daily file (one minute North and South combined) to archive

shutil.copy(path+'C_'+startdate.strftime('%Y%m%d')+'.txt',path_archive) # w-drive
shutil.copy(path+'C_'+startdate.strftime('%Y%m%d')+'.txt',path_loc_archive) # local archive


# save ten-minute file (North and South combined) as a daily file

f_tenminute = open(path+'10min_'+startdate.strftime('%Y%m%d')+'.txt','w')
for idx,rows in out_10minute.iterrows():
   out_row = ['"'+rows[0]+'"',rows[1]]  

   wd_10 = north_south_combined['wind direction 10 m sonic'][3]
   wd_2 = north_south_combined['wind 2m direction'][3]

   for iter in range(2,len(rows)):
      if (iter == wd_10) or (iter == wd_2):
          out = '%.f' % rows[iter]
          out_row.append(out+' ')

      elif (iter == 81):
           out_row.append('')
      else:
           out = '%.2f' % rows[iter]
           out_row.append(out+' ')
      
   out_row_str = ','.join(out_row)
   f_tenminute.write(out_row_str+'\n')
f_tenminute.close()

#
# copy to archive
#

shutil.copy(path+'10min_'+startdate.strftime('%Y%m%d')+'.txt',path_archive) # w-drive
shutil.copy(path+'10min_'+startdate.strftime('%Y%m%d')+'.txt',path_loc_archive) # local archive

# save hourly file (North and South combined) as a daily file

f_hour = open(path+'hour_'+startdate.strftime('%Y%m%d')+'.txt','w')
for idx,rows in out_hour.iterrows():
    out_row = [rows[0],rows[1]]  
    for iter in range(2,len(rows)-2):
       out = '%.3f' % rows[iter]
       out_row.append(out)
    for iter in range(81,89): out_row.append('')
    out_row_str = ','.join(out_row)
    f_hour.write(out_row_str+'\n')
f_hour.close()   

# copy to archive

shutil.copy(path+'hour_'+startdate.strftime('%Y%m%d')+'.txt',path_archive) # w-drive
shutil.copy(path+'hour_'+startdate.strftime('%Y%m%d')+'.txt',path_loc_archive) # local archive
 

# append daily values to monthly collection of daily statistics

if startdate.day == 1:
        # make new txt file
        newmonth = open(DataDir + 'currentmonth.txt', 'w')
        for idx,rows in out_day.iterrows():
           out_row = [rows[0],rows[1]]  
           for iter in range(2,len(rows)-2):
              out = '%.2f' % rows[iter]
              out_row.append(out)
           for iter in range(81,89): out_row.append('')
           out_row_str = ','.join(out_row)
           newmonth.write(out_row_str+'\n')  
        newmonth.close()
else:
        cm2write = open(DataDir + 'currentmonth.txt', 'a')
        for idx,rows in out_day.iterrows():
           out_row = [rows[0],rows[1]]  
           for iter in range(2,len(rows)-2):
              out = '%.2f' % rows[iter]
              out_row.append(out)
           for iter in range(81,89): out_row.append('')
           out_row_str = ','.join(out_row)
           cm2write.write(out_row_str+'\n')  
       
        cm2write.close()

# copy to local drive

shutil.copy(DataDir + 'currentmonth.txt',path+'M_'+startdate.strftime('%Y%m')+'.txt')


# copy to archive

shutil.copy(path+'M_'+startdate.strftime('%Y%m')+'.txt',path_archive) # w-drive
shutil.copy(path+'M_'+startdate.strftime('%Y%m')+'.txt',path_loc_archive) # local archive

# 
# on the first day of the month the file written by logger file
# is moved from VeenkampenNorth_stats.dat to VeenkampenNort_stats_prevmonth.dat
# Loggernet then start a 'fresh file' VeenkampenNorth_stats.dat
# VeenkampenNort_stats_prevmonth.dat is archived as VeenkampenNort_stats_YYYY_MM.dat
# the same is done for the South logger file 
#

if tm.day == 1: 
    date_prevmonth = tm-relativedelta(months=1)


# North Logger

    relpath_N = 'VeenkampenN/VeenkampenNorth_stats_'+date_prevmonth.strftime('%Y_%m')+'.dat'
    
    loc_archive_logger_file = loc_archive_rawdatadir+relpath_N
    archive_logger_file = archive_rawdatadir+relpath_N
    logger_file_prevmonth= RawdataDir+'VeenkampenNorth_stats_prevmonth.dat'
    logger_file = RawdataDir+'VeenkampenNorth_stats.dat'
   
    shutil.move(logger_file,logger_file_prevmonth) # move of VeenkampenNorth_stats.dat tot VeenkampenNorth_stats_prevmonth.dat

    shutil.copy(logger_file_prevmonth,loc_archive_logger_file) # copy of VeenkampenNorth_stats_prevmonth.dat to archive
    shutil.copy(logger_file_prevmonth,archive_logger_file) # copy of VeenkampenNorth_stats_prevmonth.dat to local archive

# South logger

    relpath_S = 'VeenkampenS/VeenkampenSouth_stats_'+date_prevmonth.strftime('%Y_%m')+'.dat'
    loc_archive_logger_file = loc_archive_rawdatadir+relpath_S
    archive_logger_file = archive_rawdatadir+relpath_S
    logger_file_prevmonth= RawdataDir+'VeenkampenSouth_stats_prevmonth.dat'

    logger_file = RawdataDir+'VeenkampenSouth_stats.dat'
    shutil.move(logger_file,logger_file_prevmonth)

    shutil.copy(logger_file_prevmonth,loc_archive_logger_file)
    shutil.copy(logger_file_prevmonth,archive_logger_file)

#
# copying to all daily files to the websever veenkampen.nl
#
make_graphs_def.make_plots(True,startdate)


subprocess.run(['c:/veenkampen/meteo/copygraphs_tometwurnl.bat',startdate.strftime('%a')])

#ESG_SB_20241213+ Removed upload to veenkampen.nl TransIP server
#cnopts = sftp.CnOpts()
#cnopts.hostkeys = None          

#try:
#  srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#  srv.cwd('www/data')
#  srv.makedirs(startdate.strftime('%Y/%m'), mode=777)  # will happily make all non-existing directories
#  srv.cwd(startdate.strftime('%Y/%m'))
#  print(srv.pwd)
#  srv.put(path+'C_'+startdate.strftime('%Y%m%d')+'.txt')
#  srv.put(path+'N'+startdate.strftime('%Y%m%d')+'.txt')
#  srv.put(path+'S'+startdate.strftime('%Y%m%d')+'.txt')
#  srv.put(path+'10min_'+startdate.strftime('%Y%m%d')+'.txt')
#  srv.put(path+'hour_'+startdate.strftime('%Y%m%d')+'.txt')
#  srv.put(path+'M_'+startdate.strftime('%Y%m')+'.txt')
#  srv.close()
#except:
#  print('no connection to  transip')
#
# here the plots are moved to the previous day
#
#
#graphs_dir = 'C:/veenkampen/meteo/graphs/'+startdate.strftime('%a')+'/'     
#files_all = glob(graphs_dir+'*png')
#
#try: 
#  srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#  srv.cwd('www/graphs/'+startdate.strftime('%a')+'/')
#  print(srv.pwd)
#  for file in files_all: srv.put(file)
#  srv.close()
#
#except:
#  print('no connection to  transip')