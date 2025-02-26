import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import datetime, timedelta
import numpy as np
import matplotlib.image as image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)

outdir = 'C:/veenkampen/fluxes/graphs/cur/'
logo_path = 'C:/veenkampen/meteo/'
FluxDir = 'C:/veenkampen_data/flux/'

logo = image.imread(logo_path + 'WUR_logo.png')
fs_title = 22
fs_labels = 19
fs_ticks = 15
fs_text = 12
fs_legend = 13
FS = 20

def make_plot_fluxes(tm):

  fg_all = pd.read_csv(FluxDir+'Eddyflux.csv',header=0)
  fg_all['datetime'] = pd.to_datetime(fg_all['date'] + ' '+fg_all['time'])+pd.Timedelta(minutes=-15)
  
  tm = tm - timedelta(minutes=tm.minute % 30, seconds=tm.second, microseconds=tm.microsecond) # rounding to start of last completed half hour

  stop = tm
  start = pd.to_datetime(stop+timedelta(days=-1))
  
  fg = fg_all.loc[fg_all['datetime'] > start]

  fg['H'] = fg['H'].where(fg['H'] > -100.,np.nan)
  fg['LE'] = fg['LE'].where(fg['LE'] > -100.,np.nan)

  fig,ax = plt.subplots(figsize=(14,6))
  ax.plot(fg['datetime'],fg['H'],color='tab:orange',lw=2,label = 'H')
  ax.plot(fg['datetime'],fg['LE'],color='tab:green',lw=2,label = 'LE')

  fg_H = fg.loc[fg['qc_H' ] == 0]
  ax.plot(fg_H['datetime'],fg_H['H'],marker='*',color='tab:orange',markersize=12,lw=0,label='qc == 0')
  fg_H = fg.loc[fg['qc_H' ] == 1]
  ax.plot(fg_H['datetime'],fg_H['H'],marker='d',color='tab:orange',markersize=12,lw=0,label='qc == 1')
  fg_H = fg.loc[fg['qc_H' ] == 2]
  ax.plot(fg_H['datetime'],fg_H['H'],marker='o',color='tab:orange',markersize=12,lw=0,label='qc == 2')

  fg_LE = fg.loc[fg['qc_LE' ] == 0]
  ax.plot(fg_LE['datetime'],fg_LE['LE'],marker='*',color='tab:green',markersize=12,lw=0) # label='qc == 0')
  fg_LE = fg.loc[fg['qc_LE' ] == 1]
  ax.plot(fg_LE['datetime'],fg_LE['LE'],marker='d',color='tab:green',markersize=12,lw=0) # ,label='qc == 1')
  fg_LE = fg.loc[fg['qc_LE' ] == 2]
  ax.plot(fg_LE['datetime'],fg_LE['LE'],marker='o',color='tab:green',markersize=12,lw=0) # ,label='qc == 2')
 
  leg = ax.legend(loc='upper right',bbox_to_anchor=(1.15, 1), fontsize=fs_legend)
  leg.legendHandles[2].set_color('black')
  leg.legendHandles[3].set_color('black')
  leg.legendHandles[4].set_color('black')

  ax.set_ylabel('$W m^{-2}$',fontsize=fs_labels)
  ax.set_xlabel('Time [UTC]',fontsize=fs_labels)
  plt.title('Energy Fluxes', fontsize=fs_title, pad=45)
  plt.grid(color='gainsboro', linestyle='--', which='both')  
  
  ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
  ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
  ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
  ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))

  ax.set_xlim([start,stop])

  for item in ([ax.xaxis.label, ax.yaxis.label ] + ax.get_xticklabels(which='major') + ax.get_yticklabels() + ax.get_legend().get_texts()): 
      item.set_fontsize(fs_ticks)
  imagebox = OffsetImage(logo, zoom=0.5)
  ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
  ax.add_artist(ab)
  plt.tight_layout() #rect=[0, 0.0, 1.05, 1.])    # [left, bottom, right, top]  
  plt.savefig(outdir+'Fluxes.png',format='png')

def make_plot_co2_h2o_flux(tm):

  fg_all = pd.read_csv(FluxDir+'Eddyflux.csv',header=0)
  fg_all['datetime'] = pd.to_datetime(fg_all['date'] + ' '+fg_all['time'])+pd.Timedelta(minutes=-15)
 
  stop = tm
  start = pd.to_datetime(stop+timedelta(days=-1))
  
  fg = fg_all.loc[fg_all['datetime'] > start]
  fg['co2_flux'] = fg['co2_flux'].where(fg['co2_flux'] > -100.,np.nan)
  fg['h2o_flux'] = fg['h2o_flux'].where(fg['h2o_flux'] > -100.,np.nan)

  fig,ax = plt.subplots(figsize=(13, 6))
  lns1 = ax.plot(fg['datetime'],fg['co2_flux'],color='tab:orange',lw=2,label = '$CO_2$')
  ax.set_ylabel('$CO_2$ flux [$\mu$mol $m^{-2}$ $s^{-1}$]',fontsize=fs_labels,color='tab:orange')
  
  ax2 = ax.twinx()
  lns2 = ax2.plot(fg['datetime'],fg['h2o_flux'],color='tab:green',lw=2,label = '$H_2O$')
  ax2.set_ylabel('$H_2O$ flux [mmol $m^{-2}$ $s^{-1}$]',fontsize=fs_labels,color='tab:green')
  
  fg_co2 = fg.loc[fg['qc_co2_flux' ] == 0]
  lns3 = ax.plot(fg_co2['datetime'],fg_co2['co2_flux'],marker='*',color='tab:orange',markersize=12,lw=0,label='qc == 0')
  fg_co2 = fg.loc[fg['qc_co2_flux' ] == 1]
  lns4 = ax.plot(fg_co2['datetime'],fg_co2['co2_flux'],marker='d',color='tab:orange',markersize=12,lw=0,label='qc == 1')
  fg_co2 = fg.loc[fg['qc_co2_flux' ] == 2]
  lns5 = ax.plot(fg_co2['datetime'],fg_co2['co2_flux'],marker='o',color='tab:orange',markersize=12,lw=0,label='qc == 2')

  fg_h2o = fg.loc[fg['qc_h2o_flux' ] == 0]
  ax2.plot(fg_h2o['datetime'],fg_h2o['h2o_flux'],marker='*',color='tab:green',markersize=12,lw=0) # label='qc == 0')
  fg_h2o = fg.loc[fg['qc_h2o_flux' ] == 1]
  ax2.plot(fg_h2o['datetime'],fg_h2o['h2o_flux'],marker='d',color='tab:green',markersize=12,lw=0) # ,label='qc == 1')
  fg_h2o = fg.loc[fg['qc_h2o_flux' ] == 2]
  ax2.plot(fg_h2o['datetime'],fg_h2o['h2o_flux'],marker='o',color='tab:green',markersize=12,lw=0) # ,label='qc == 2')
  
  plt.title('Carbon dioxide and water vapour fluxes', fontsize=fs_title, pad=30)
  ax.grid(color='gainsboro', linestyle='--', which='both')
  ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
  ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
  ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
  ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))

  ax.set_xlabel('Time [UTC]',fontsize=fs_labels)
  ax.set_xlim([start,stop])
 
  labs = [l.get_label() for l in lns1+lns2+lns3+lns4+lns5]
  leg = ax.legend(lns1+lns2+lns3+lns4+lns5,labs,bbox_to_anchor=(1.3, 1), fontsize=fs_legend)
  leg.legendHandles[2].set_color('black')
  leg.legendHandles[3].set_color('black')
  leg.legendHandles[4].set_color('black')

#for tick in ax.xaxis.get_major_ticks():
#     tick.label1.set_fontweight('bold')
  
  for item in ([ax.xaxis.label, ax.yaxis.label,ax2.yaxis.label ] + ax.get_xticklabels(which='major') + ax.get_yticklabels() + ax.get_legend().get_texts()): 
     item.set_fontsize(fs_ticks)
  
  imagebox = OffsetImage(logo, zoom=0.5)
  ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
  ax.add_artist(ab)
   
  plt.tight_layout()
  plt.savefig(outdir+'co2h2oflux.png',format='png')

def make_plot_co2_h2o_conc(tm):

  fg_all = pd.read_csv(FluxDir+'Eddyflux.csv',header=0)
  fg_all['datetime'] = pd.to_datetime(fg_all['date'] + ' '+fg_all['time'])+pd.Timedelta(minutes=-15)

  stop = tm
  start = pd.to_datetime(stop+timedelta(days=-1))
 
  fg = fg_all.loc[fg_all['datetime'] > start]
  fg['co2_mole_fraction'] = fg['co2_mole_fraction'].where(fg['co2_mole_fraction'] > -100.,np.nan)
  fg['h2o_mole_fraction'] = fg['h2o_mole_fraction'].where(fg['h2o_mole_fraction'] > -100.,np.nan)
  
  fig,ax = plt.subplots(figsize=(13, 6))
  lns1 = ax.plot(fg['datetime'],fg['co2_mole_fraction'],color='tab:orange',lw=2,label = '$CO_2$')
  ax.set_ylabel('$CO_2$ conc [ppm]',fontsize=fs_labels,color='tab:orange')
  ax2 = ax.twinx()
  lns2 = ax2.plot(fg['datetime'],fg['h2o_mole_fraction'],color='tab:green',lw=2,label = '$H_2O$')
  ax2.set_ylabel('$H_2O$ conc [ppt]',fontsize=fs_labels,color='tab:green')
  
  ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
  ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
  ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
  ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))

  ax.set_xlabel('Time [UTC]',fontsize=fs_labels)
  ax.set_xlim([start,stop])

  labs = [l.get_label() for l in lns1+lns2]
  leg = ax.legend(lns1+lns2,labs,bbox_to_anchor=(1.2, 1), fontsize=fs_legend)
  plt.title('Carbon dioxide and water vapour concentration', fontsize=fs_title, pad=30)
#for tick in ax.xaxis.get_major_ticks():
#     tick.label1.set_fontweight('bold')
  for item in ([ax.xaxis.label, ax.yaxis.label,ax2.yaxis.label ] + ax.get_xticklabels(which='major') + ax.get_yticklabels() + ax.get_legend().get_texts()): 
      item.set_fontsize(fs_ticks)
  
  imagebox = OffsetImage(logo, zoom=0.5)
  ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
  ax.add_artist(ab)
   
  plt.tight_layout()
  plt.savefig(outdir+'co2h2oconc.png',format='png')