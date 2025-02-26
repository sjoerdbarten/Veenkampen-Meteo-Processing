import numpy as np
import os
import shutil
from glob import glob
import subprocess
from datetime import datetime,timedelta
import pysftp as sftp
import make_plots
from pathlib import Path
import pandas as pd

#
# directory to find the raw data
#

raw_datadir = 'C:/Veenkampen/Data/Baler/Data/CR1000_EC/'

#
# directory where the raw data is stored
#

raw_datadir_store = raw_datadir+'Store/'

#
# directories for archiving the raw data from Baler
#

archive_raw_datadir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/raw_data/EC/Baler/' #w-drive
loc_archive_raw_datadir = 'D:/veenkampen_archive/raw_data/EC/baler/' # local archive


#
# directories to put the data 
#

DataDir = 'C:/veenkampen_data/' # daily file of fluxes
FluxDir = 'C:/veenkampen_data/flux/' # file with combined output of eddypro file

#
# archive datadir to store the combined output from eddypro.
#

archive_fluxdir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/veenkampen_data/flux/' #w-drive
loc_archive_fluxdir = 'D:/Veenkampen_archive/veenkampen_data/flux/' # local archive

#
# archive directores of daily files fo fluxes
#

archive_datadir = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/veenkampen_data/' #w-drive
loc_archive_datadir = 'D:/veenkampen_archive/veenkampen_data/' #local archive


#
# backup data directory from loggernet (TOB1 files)
#
 
raw_datadir_backup = 'C:/Veenkampen/Data/' # local
archive_datadir_backup = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/raw_data/EC/EC_CR1000/' # w-drivearchive
loc_archive_datadir_backup = 'D:/veenkampen_archive/raw_data/EC/EC_CR1000/'  # local archive
 
date_now_UTC = datetime.utcnow() # find time now
tm= date_now_UTC+timedelta(minutes=-30) # shift 30 minutes to get last output file from Baler.exe
tm = tm - timedelta(minutes=tm.minute % 30, seconds=tm.second, microseconds=tm.microsecond) # rounding to start of last completed half hour
daypassed=False

if (tm.hour == 23) & (tm.minute == 30): daypassed=True # find out whether day has finished

# 
# define the last file produced by Baler.exe
#

latest_raw_file = raw_datadir+'raw_data_'+tm.strftime('%Y_%m_%d_%H%M')+'.dat'

#
# if the file exists do the processing
# else add a line eddyflux.csv indicating that the output file from Baler is missing
#
if Path(latest_raw_file).is_file():
 
# define the local directory

   dest = 'C:/veenkampen/fluxes'

#
# copy the last 4 output files from Baler.exe if available
#
 
   for x in range(4):
     delt = x*30
     file = raw_datadir+'raw_data_'+(tm+timedelta(minutes=-delt)).strftime('%Y_%m_%d_%H%M')+'.dat'
     if Path(file).is_file(): 
        shutil.copy(file,dest)
 
#
# move the oldest file available to the Store directory to avoid that 
# eddypro uses two many files
#
        if x == 3: shutil.move(file,raw_datadir_store) 
   
 
#
# start eddypro
#
   print('eddypro starting')
 
#
# eddypro is launched with as argument 'c:/veenkampen/fluxes/ini/EC_VK.eddypro' to define that
# eddypro should use EC_VK.eddypro as ini file
#

   prun = subprocess.run(['C:/veenkampen/EddyPro-7.0.9/bin/eddypro_rp.exe','c:/veenkampen/fluxes/ini/EC_VK.eddypro'])


#
# get a list  of all full_output* eddypro output files
#

   list_of_eddypro_output = glob(r'c:/veenkampen/eddypro-7.0.9/output/*full_output*.csv') 

#
# find the latest eddypro full output file
#

   latest_file = max(list_of_eddypro_output, key=os.path.getctime) 

# open the latest eddypro full output file
 
   fin = open(latest_file)
   lines = fin.readlines()
   fin.close()

#
# check whether the last line of the latest eddypro full output file refers to the expected latest baler output file

   date_eddy_pro = lines[-1].split(',')[1]
   time_eddy_pro = lines[-1].split(',')[2]
# 
# if the last line f the latest eddypro full output file refers to the expected latest baler output file
# add  the last line to eddypro.csv
# else issue an error message, that eddypro did not run, ad write an line with -999. values to eddypro.csv 
#

   if (date_eddy_pro == (tm+timedelta(minutes=30)).strftime('%Y-%m-%d')) & (time_eddy_pro == (tm+timedelta(minutes=30)).strftime('%H:%M')): 
      line_out = lines[-1]
   else:
      err_msg = 'no_eddypro_file:'+tm.strftime('%Y_%m_%d_%H%M')+','
      line1 = err_msg+(tm+timedelta(minutes=30)).strftime('%Y-%m-%d,%H:%M')+',-999'*112+'\n'
      line_out = line1


else:
  err_msg = 'no_raw_file:'+tm.strftime('%Y_%m_%d_%H%M')+','
  line1 = err_msg+(tm+timedelta(minutes=30)).strftime('%Y-%m-%d,%H:%M')+',-999'*112+'\n'
  line_out = line1


# 
# read the current eddypro.csv file
#

f_eddy = open(FluxDir+'Eddyflux.csv','r')
eddy_lines = f_eddy.readlines()
f_eddy.close()  

# delete the first line with data (not the header) to 
# avoid too large files
#

del eddy_lines[1]

#
# write eddypro.csv with a removed first dataline
# and a new line with the newest calculation
#

f_eddy = open(FluxDir+'Eddyflux.csv','w')
lines2write = eddy_lines + [line_out]
f_eddy.writelines(lines2write)
f_eddy.close()

f_eddy_csv = pd.read_csv(FluxDir+'Eddyflux.csv',header=0)
f_eddy_csv.to_csv(FluxDir+'Eddyflux_backup.csv',index=False)
f_eddy_csv['date'] = pd.to_datetime(f_eddy_csv.date)
f_eddy_csv['date'] = f_eddy_csv['date'].dt.strftime("%Y-%m-%d")
f_eddy_csv.to_csv(FluxDir+'Eddyflux.csv',index=False)

#
# copy the eddyflux.cav file to the archive
#

shutil.copy(FluxDir+'Eddyflux.csv',archive_fluxdir) # w-drive
shutil.copy(FluxDir+'Eddyflux.csv',loc_archive_fluxdir) # local archive

#
# make the plots
#

make_plots.make_plot_fluxes(date_now_UTC)
make_plots.make_plot_co2_h2o_flux(date_now_UTC)
make_plots.make_plot_co2_h2o_conc(date_now_UTC)


#
# remove the copies of the raw baler files in the 
# working directory
#

file_list = glob('./raw_data*')
for file in file_list:
  try:
     os.remove(file)
  except:
      print(file+': cannot be removed')


# 
# make a copy of the latest TOB1 file produced by Loggernet to the archive
#

shutil.copy(raw_datadir_backup+'ECraw_VK.dat',archive_datadir_backup) #w-drive
shutil.copy(raw_datadir_backup+'ECraw_VK.dat',loc_archive_datadir_backup) # local archive


# 
# send the fluxes graphs for publication on veenkampen.nl/graphs/cur
#

os.system('copygraphs.bat cur')

cnopts = sftp.CnOpts()
cnopts.hostkeys = None   
outgraphs = 'c:/veenkampen/fluxes/graphs/cur/'

#try:
#  srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#  #srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
#  srv.cwd('www/graphs/cur/')
#  srv.put(outgraphs+'co2h2oflux.png')
#  srv.put(outgraphs+'co2h2oconc.png')
#  srv.put(outgraphs+'Fluxes.png')
#  srv.close()
#except:
#  print('no conection to transip server')

#
# to old met.wur.nl server
#
#ESG_SB_20241213+ Removed double call of copygraphs.bat
#os.system('copygraphs.bat cur')

#
#ESG_SB_20231110+ Added live upload of flux data (everytime the script is called) to the veenkampen.nl/data 'home' folder
#

date_str = tm.strftime('%Y%m%d')
date_str_infile = tm.strftime('%Y_%m_%d')

cur_live = open(FluxDir+'Eddyflux.csv','r')
lines_live = cur_live.readlines()

live_upload = []
for line_upload in lines_live[-48:]: 
  live_upload.append(line_upload)

path = DataDir
os.makedirs(path,exist_ok=True)
 
path_archive = 'W:/ESG/DOW_MAQ/MAQ_Archive/Veenkampen_archive/veenkampen_data/flux/' #w-drive
os.makedirs(path_archive,exist_ok=True)

path_loc_archive = 'D:/Veenkampen_archive/veenkampen_data/flux/' # local archive
os.makedirs(path_loc_archive,exist_ok=True)
 
fout = open(path+'flux_current.txt','w')
for line_upload2 in live_upload: fout.write(line_upload2)
fout.close()

shutil.copy(path+'flux_current.txt',path_archive) # w-drive
shutil.copy(path+'flux_current.txt',path_loc_archive) # local archive

#ESG_SB_20241213+ Removed upload to veenkampen.nl TransIP server
#try:
#   cnopts = sftp.CnOpts()
#   cnopts.hostkeys = None
#   srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#   srv.cwd('/data/sites/web/veenkampennl/www/data')
#   srv.put(path+'flux_current.txt')
#   srv.close()
#except:
#   print('no connection with transip server')

#
#ESG_SB_20231110- Added live upload of flux data (everytime the script is called) to the veenkampen.nl/data 'home' folder
#

# if the day is passed do some extra management

if daypassed:
    print('daypassed')

#
# find all lines in eddypro.csv that refer to raw Baler raw datafiles
# that refer to the previous day
#  
    os.system('copygraphs.bat '+tm.strftime('%a'))
    date_str = tm.strftime('%Y%m%d')
    date_str_infile = tm.strftime('%Y_%m_%d')

    f = open(FluxDir+'Eddyflux.csv','r')
    lines = f.readlines()

    yest_lines = []
    for line in lines: 
       if date_str_infile in line.split(',')[0]: yest_lines.append(line)

#
# define the directory where the daily file need to be stored
#
    path = os.path.join(DataDir,tm.strftime('%Y/%m/'))
    os.makedirs(path,exist_ok=True)

#
# define the path where the daily file need  to be arvchived
#
 
    path_archive = os.path.join(archive_datadir,tm.strftime('%Y/%m/')) #w-drive
    os.makedirs(path_archive,exist_ok=True)

    path_loc_archive = os.path.join(loc_archive_datadir,tm.strftime('%Y/%m/')) # local archive
    os.makedirs(path_loc_archive,exist_ok=True)

#
# write the daily file to the local directory
#
  
    fout = open(path+'flux_'+date_str+'.txt','w')
    for line in yest_lines: fout.write(line)
    fout.close()

#
# copy the daily file to the archive
#

    shutil.copy(path+'flux_'+date_str+'.txt',path_archive) # w-drive
    shutil.copy(path+'flux_'+date_str+'.txt',path_loc_archive) # local archive

#
# copy the ECraw_VK.dat TOB1 file from loggernet to the archive as a daily file of loggernet data
#
    shutil.copy(raw_datadir_backup+'ECraw_VK.dat',archive_datadir_backup+'ECraw_VK_'+tm.strftime('%Y_%m_%d')+'.dat') # w-drive
    shutil.copy(raw_datadir_backup+'ECraw_VK.dat',loc_archive_datadir_backup+'ECraw_VK_'+tm.strftime('%Y_%m_%d')+'.dat') # local archive

#
# if the copying is done succesfull, rempve ECraw_VK, so that Loggernet creates a 'fresh' Loggernet file
#    
    if Path(archive_datadir_backup+'ECraw_VK_'+tm.strftime('%Y_%m_%d')+'.dat').is_file(): os.remove(raw_datadir_backup+'ECraw_VK.dat')
    
#
# define the day before yesterday
#
    tm_beforeyest = tm+timedelta(days=-1)

#
# zip all raw datafiles produced on the day before yesterday by Baler.exe into a zip ECraw_VK_YYYMMDD.7z
#
    os.system('7z.exe a '+raw_datadir_store+'ECraw_VK_'+tm_beforeyest.strftime('%Y%m%d')+'.7z '+raw_datadir_store+'raw_data_'+tm_beforeyest.strftime('%Y_%m_%d')+'_*.dat')

#
# make directories for archiving the 7z file 
#
    path_archive = os.path.join(archive_raw_datadir,tm_beforeyest.strftime('%Y/')) # w-drive
    os.makedirs(path_archive,exist_ok=True)

    path_loc_archive = os.path.join(loc_archive_raw_datadir,tm_beforeyest.strftime('%Y/')) # local archive
    os.makedirs(path_loc_archive,exist_ok=True)

#
# copy the 7z files into the archive
#
 
    shutil.copy(raw_datadir_store+'ECraw_VK_'+tm_beforeyest.strftime('%Y%m%d')+'.7z',path_archive) # w-drive
    shutil.copy(raw_datadir_store+'ECraw_VK_'+tm_beforeyest.strftime('%Y%m%d')+'.7z',path_loc_archive) # local archive

#
# copy the daily file to the webserver, and also the most recent .7z file
#
#ESG_SB_20241213+ Removed upload to veenkampen.nl TransIP server
#    try:
#      cnopts = sftp.CnOpts()
#      cnopts.hostkeys = None      
# 
## send daily file to webserver
#  
#      #srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
#      srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#      srv.cwd('/data/sites/web/veenkampennl/www/data')
#      srv.makedirs(tm.strftime('%Y/%m'), mode=777)  # will happily make all non-existing directories
#      srv.cwd(tm.strftime('%Y/%m'))
#      srv.put(path+'flux_'+date_str+'.txt')
#
## send the latest 7z file to webserver
#
#      srv.cwd('/data/sites/web/veenkampennl/www/flux')
#      srv.makedirs(tm_beforeyest.strftime('%Y'),mode=777)
#      srv.cwd(tm_beforeyest.strftime('%Y'))
#      srv.put(raw_datadir_store+'ECraw_VK_'+tm_beforeyest.strftime('%Y%m%d')+'.7z')
#      srv.close()
#
## send the graphs of yesterday to the webserver
#    
#    #  srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
#      srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#      srv.cwd('www/graphs/'+tm.strftime('%a')+'/')
#      srv.put(outgraphs+'co2h20flux.png')
#      srv.put(outgraphs+'co2h2oconc.png')
#      srv.put(outgraphs+'Fluxes.png')
#      srv.close()
#    except:
#      print('no connection with transip server')
