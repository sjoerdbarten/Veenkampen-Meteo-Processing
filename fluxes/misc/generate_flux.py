import numpy as np
import subprocess
import os
import shutil
from glob import glob
import subprocess
from datetime import datetime,timedelta
import pysftp as sftp
import make_plots

DataDir = 'C:/veenkampen_data/data_exp/'
FluxDir = 'C:/veenkampen_data/flux_exp/'

date_now_UTC = datetime.utcnow()
tm= date_now_UTC+timedelta(minutes=-30)
tm = tm - timedelta(minutes=tm.minute % 30, seconds=tm.second, microseconds=tm.microsecond)
daypassed=False

if (tm.hour == 23) & (tm.minute == 30): daypassed=True
print('start')
try:
  source = 'C:/Veenkampen/Data/Baler/Data/CR1000_EC/raw_data_'+tm.strftime('%Y_%m_%d_%H%M')+'.dat'
  dest = 'C:/veenkampen/fluxes'
  dest_store = 'C:/Veenkampen/Data/Baler/Data/CR1000_EC/store'
  for x in range(4):
    print(x)
    delt = x*30
    source = 'C:/Veenkampen/Data/Baler/Data/CR1000_EC/raw_data_'+(tm+timedelta(minutes=-delt)).strftime('%Y_%m_%d_%H%M')+'.dat'
    print(source)
    shutil.copy(source,dest)  
    if x == 3: 
      shutil.move(source,dest_store)
    print('here')
  print('eddypro starting')
  prun = subprocess.run(['C:/veenkampen/EddyPro-7.0.9/bin/eddypro_rp.exe','c:/veenkampen/fluxes/ini/EC_VK.eddypro'])
  os.system('del raw*')
  
  list_of_eddypro_output = glob('c:/veenkampen/eddypro-7.0.9/output/*full_output*.csv') # * means all if need specific format then *.csv   
  latest_file = max(list_of_eddypro_output, key=os.path.getctime) 
  
  print('Latest eddypro file: '+latest_file)
  
  fin = open(latest_file)
  lines = fin.readlines()
  
  line_out = lines[-1]
  fin.close()
  
except:
  print(date_now_UTC.strftime('%Y%m%d_%H')+' not available')
  err_msg = 'no_raw_file:'+tm.strftime('%Y_%m_%d_%H')+'00.dat,'
  line1 = err_msg+tm.strftime('%Y-%m-%d,%H')+':30'+',-999'*112+'\n'

  line_out = line1

f_eddy = open(FluxDir+'Eddyflux.csv','r')
eddy_lines = f_eddy.readlines()
f_eddy.close()

del eddy_lines[1]

f_eddy = open(FluxDir+'Eddyflux.csv','w')
lines2write = eddy_lines + [line_out]
f_eddy.writelines(lines2write)
f_eddy.close()

make_plots.make_plot_fluxes(date_now_UTC)
make_plots.make_plot_co2_h2o_flux(date_now_UTC)
make_plots.make_plot_co2_h2o_conc(date_now_UTC)

cnopts = sftp.CnOpts()
cnopts.hostkeys = None   
outgraphs = 'c:/veenkampen/fluxes/graphs/cur/'
srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
#srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
srv.cwd('www/graphs_exp/cur/')
#srv.put(outgraphs+'BC_24.png','BC.png')
srv.put(outgraphs+'co2h20flux.png')
srv.put(outgraphs+'co2h2oconc.png')
srv.put(outgraphs+'Fluxes.png')
srv.close()

if daypassed:
    print('daypassed')
  

    date_str = tm.strftime('%Y%m%d')
    date_str_infile = tm.strftime('%Y_%m_%d')

    f = open(FluxDir+'Eddyflux.csv','r')
    lines = f.readlines()

    yest_lines = []
    for line in lines: 
       if 'raw_data_'+date_str_infile in line.split(',')[0]: yest_lines.append(line)

    path = os.path.join(DataDir,tm.strftime('%Y/%m/'))
    os.makedirs(path,exist_ok=True)
  
    fout = open(path+'flux_'+date_str+'.txt','w')
    for line in yest_lines: fout.write(line)
    fout.close()

    cnopts = sftp.CnOpts()
    cnopts.hostkeys = None      
   
    srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
    #srv = sftp.Connection(host="veenkampen.nl.transurl.nl",username="veenkampen.nl",password="MAQ_transip_2021",cnopts=cnopts)
    srv.cwd('/www/data_exp')
    srv.makedirs(tm.strftime('%Y/%m'), mode=777)  # will happily make all non-existing directories
    srv.cwd(tm.strftime('%Y/%m'))
    print(srv.pwd)
    srv.put(path+'flux_'+date_str+'.txt')
    srv.close()