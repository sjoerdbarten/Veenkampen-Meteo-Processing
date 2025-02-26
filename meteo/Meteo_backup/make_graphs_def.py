import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from windrose import WindroseAxes
from matplotlib import cm
import matplotlib.dates as dates
pd.plotting.register_matplotlib_converters()    # to register converter
from PIL import Image

def make_plots(dayproc,tm):
   
    # *** Directories ***
    datadir = 'C:/veenkampen/meteo/graphs/'
   
    ccurrent_path = 'C:/veenkampen_data/'
    logo_path = 'C:/veenkampen/meteo/'
    
    # *** Load C_current.txt ***
    if dayproc:
       print('dayproc')
       ccurrent_path = ccurrent_path+'data_exp/'+tm.strftime('%Y/%m/')
       datadir = datadir+tm.strftime('%a')+'/'
       cfile = pd.read_csv(ccurrent_path + 'C_'+tm.strftime('%Y%m%d.txt'), header=None, sep=',', parse_dates=[[0, 1]],
                        na_values=-999., dtype='float')
    else:
       ccurrent_path = ccurrent_path+'data_exp/'
       cfile = pd.read_csv(ccurrent_path + 'C_current.txt', header=None, sep=',', parse_dates=[[0, 1]],
                        na_values=-999., dtype='float')
       datadir = datadir+'cur/'
    print('ccurrent: ',ccurrent_path)
    print('datadir: ',datadir)
    cfile.index = cfile['0_1'].values                   # set date as index
    ccurrent = cfile.drop(cfile.columns[0], axis=1)     # remove date column that is not the index
    xlim = ccurrent.index[0]+pd.Timedelta(minutes=-1)
    # *** Make graphs ***
    logo = image.imread(logo_path + 'WUR_logo.png')
    xaxis_ticks = ['{:02d}'.format(jj) for jj in ccurrent.index.hour[::60]]
    if dayproc:
       date_text = ccurrent.index[0].day_name() + '    ' + ccurrent.index[0].strftime('%d-%m-%Y')
    else:
       date_text = ccurrent.index[-1].day_name() + '    ' + ccurrent.index[-1].strftime('%d-%m-%Y')
    fs_title = 22
    fs_labels = 19
    fs_ticks = 15
    fs_text = 12
    fs_legend = 12    # changed 20230227 by KvdD from 13 to 12 overlapping legend with graphs
    
    fig_dpi = 80      #ESG_SB_20230831+ Added fig_dpi to more easily change resolution and file size of all figures
 
    # Temperature: col. 2 (dry bulb), col. 70 (wet bulb), col. 6 (shielded), col. 67 (dew point)
    tmin = ccurrent[4].min() #20230225 it was Twet, changed to Tdry_unventilated (5 changed to 4)
    tmax = ccurrent[4].max() #,,
    tmean_last10min = ccurrent[4][-11:].mean()#,,
    # check if values nan for text display
    if np.isnan(tmin) or np.isnan(tmax):
        textminmax = '$T_{min}$ and $T_{max}$ over last 24 hours: -'
    else:
        textminmax = '$T_{min}$ and $T_{max}$ over last 24 hours: %.1f °C and %.1f °C' % (tmin, tmax)

    if np.isnan(tmean_last10min):
        textmean = '$T_{mean}$ over last 10 minutes: -'
    else:
        textmean = '$T_{mean}$ over last 10 minutes: %.1f °C' % tmean_last10min
    # compute wet bulb and dew point
    wetbulb = ccurrent[7].values * np.arctan(0.151977 * (ccurrent[8].values + 8.3133659) ** 0.5) \
              + np.arctan(ccurrent[7].values + ccurrent[8].values) - np.arctan(ccurrent[8].values - 1.676331) \
              + 0.0039838 * ccurrent[8].values ** 1.5 * np.arctan(0.023101 * ccurrent[8].values) - 4.686035 #20230225 changed from 2 to 7 (to Tvaisala)
            # 20230322 changed by KvdD the above value 0.023101 from its origenal 0.03101(see Stull) his error was found by Frits Antonysen !!!!!
    dewpoint = (ccurrent[8] / 100.) ** (1./8.) * (112. + 0.9 * ccurrent[7]) + 0.1 * ccurrent[7] - 112.#20230225 changed from 2 to 7 (to Tvaisala)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(ccurrent.index.values, ccurrent[4].values, color='goldenrod', label='Dry bulb(+150 cm)', linewidth=2)#20230225 2 changed to 4 (to Tdry_unvent north hut
    ax.plot(ccurrent.index.values, wetbulb, color='darkturquoise', label='Wet bulb(+150 cm, computed)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[6].values, color='deeppink', label='Shielded(+10 cm)', linewidth=2)
    ax.plot(ccurrent.index.values, dewpoint.values, color='darkblue', label='Dew point(+150 cm, computed)', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.39, 1), fontsize=fs_legend)      #changed 20230313 by KvdD changed from 1.39 to 1.43 for Python311 and for Python3.9 back to 1.39
    plt.ylabel('Temperature [°C]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Temperature', fontsize=fs_title, pad=45)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    plt.text(0.26, 1.065, textminmax, transform=ax.transAxes, fontsize=fs_text)
    plt.text(0.35, 1.02, textmean, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout(rect=[0, 0.0, 1.05, 1.])    # [left, bottom, right, top]
    plt.savefig(datadir + 'Temp.png', dpi=fig_dpi)
    plt.close()

    # Humidity: col. 8
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[8].values, color='firebrick', linewidth=2)
    plt.ylabel('Relative Humidity [%]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Humidity', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Humidity.png', dpi=fig_dpi)
    plt.close()

    # Pressure: col. 21
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[21].values, color='mediumblue', linewidth=2)
    plt.ylabel('Pressure [kPa]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Pressure', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Pressure.png', dpi=fig_dpi)
    plt.close()

    # Precipitation: col. 63-44 (sum) and col. 57 (intensity)
    rain_sum = ccurrent[63-44].cumsum()
    rain_sum = ccurrent[57].cumsum()

    fig, ax = plt.subplots(figsize=(13, 6))
    ax2 = ax.twinx()
    ax2.plot(ccurrent.index.values, ccurrent[57].values, color='mediumblue', linewidth=2)
    ax2.set_ylabel('Intensity [mm/min]', fontsize=fs_labels, color='mediumblue')
  #  ax.plot(ccurrent.index.values, ccurrent[63-44].values, color='firebrick', linewidth=2)
    ax.plot(ccurrent.index.values, rain_sum.values, color='firebrick', linewidth=2)
 
    ax.set_ylabel('Total precipitation [mm]', fontsize=fs_labels, color='firebrick')
    ax.set_xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Precipitation', fontsize=fs_title, pad=30)
    ax.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels() + ax2.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    ax.set_ylim(0., rain_sum.max()+2.5)     #CHANGED 20230605 by KvdD from +0.1 to +2.5  not nearly full scale after a few drops
    ax2.set_ylim(0., ccurrent[57].max()+0.4)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    plt.text(0.38, 1.02, 'Total over last 24 hours: %.2f mm' % rain_sum[-1], transform=ax.transAxes, fontsize=fs_text)
#    plt.text(0.38, 0.60, 'Cables of precipitation sensor broken by vole.\nWill be repaired soon.', transform=ax.transAxes, fontsize=fs_text)  #ESG_SB_20230801 Temporary text box
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
#    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Rain.png', dpi=fig_dpi)
    plt.close()

    # Tgrass=Temperature under grass: col. 31 (5cm), col. 32 (10cm), col. 33 (20cm), col. 35 (100cm), col. 36 (150cm)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[31].values, color='goldenrod', label='5 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[32].values, color='brown', label='10 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[33].values, color='deeppink', label='20 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[35].values, color='darkblue', label='100 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[36].values, color='darkturquoise', label='150 cm', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.14, 1), fontsize=fs_legend)
    plt.ylabel('Temperature [°C]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Temperature under grass', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Tgrass.png', dpi=fig_dpi)
    plt.close()

    # Tbare= Temp. under bare soil: col. 37 (5cm), col. 38 (10cm), col. 39 (20cm), col. 40 (50cm)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[37].values, color='seagreen', label='5 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[38].values, color='gold', label='10 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[39].values, color='darkturquoise', label='20 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[40].values, color='mediumblue', label='50 cm', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.14, 1), fontsize=fs_legend)
    plt.ylabel('Temperature [°C]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Temperature under bare soil', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    plt.text(1.015, 0.52, '10 cm and 20 cm \nsensors broken by \nlightning, waiting \nfor repair.',
             transform=ax.transAxes, fontsize=fs_text, bbox=dict(boxstyle='round', facecolor='none', ec='lightgrey'))
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Tbare.png', dpi=fig_dpi)
    plt.close()

    # Heatflux: col. 41 (side1), col. 42 (side2), col. 43 (side3), col. 44 (side4 (bare soil))
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[41].values, color='seagreen', label='side 1 (grass)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[42].values, color='deeppink', label='side 2 (grass)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[43].values, color='darkturquoise', label='side 3 (grass)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[44].values, color='mediumblue', label='side 4 (bare soil)', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1), fontsize=fs_legend)
    plt.ylabel('Heat flux [$Wm^{-2}$]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Soil heat flux (at 6 cm below ground level)', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Heatflux.png', dpi=fig_dpi)
    plt.close()

    # Radiation1: col. 9 (Qglb in), col. 10 (Qglb out), col. 11 (Qlong in), col. 12 (Qlong out), col. 13 (Qnet)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[9].values, color='goldenrod', label='Q Short (in)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[10].values, color='firebrick', label='Q Short (out)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[11].values, color='darkturquoise', label='Q Long (in)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[12].values, color='mediumblue', label='Q Long (out)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[13].values, color='deeppink', label='Q Net', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1), fontsize=fs_legend)
    plt.ylabel('Radiation [$Wm^{-2}$]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Radiation 1', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Radiation.png', dpi=fig_dpi)
    plt.close()

    # Radiation2: col. 9 (Qlb in), col. 15 (Q beam tracker), col. 14 (Q diffuse)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[9].values, color='goldenrod', label='Q Short (in)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[15].values, color='forestgreen', label='Q Direct (normal beam)', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[14].values, color='darkorchid', label='Q Diffuse (in)', linewidth=2)
    plt.legend(loc='upper right', bbox_to_anchor=(1.35, 1), fontsize=fs_legend)
    plt.ylabel('Radiation [$Wm^{-2}$]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Radiation 2', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Radiation2.png', dpi=fig_dpi)
    plt.close()

    # Sunshine: col. 17
    if dayproc:
      duration_hour = int(ccurrent[17][ccurrent[17].index.day == ccurrent.index[0].day].sum() / 3600.)   # only today
      duration_min = int(((ccurrent[17][ccurrent[17].index.day == ccurrent.index[0].day].sum() / 3600.)
                        - duration_hour) * 60.)
    else:
      duration_hour = int(ccurrent[17][ccurrent[17].index.day == ccurrent.index[-1].day].sum() / 3600.)   # only today
      duration_min = int(((ccurrent[17][ccurrent[17].index.day == ccurrent.index[-1].day].sum() / 3600.)
                        - duration_hour) * 60.)
  #  duration_hour = int(ccurrent[17].sum() / 3600.)   # only today
  #  duration_min = int(((ccurrent[17].sum() / 3600.)
  #                      - duration_hour) * 60.)
  
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[17].values, color='red', marker='.', markersize=9, linewidth=0)
    plt.ylabel('Sunshine duration [s/min]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Sunshine duration', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    plt.text(0.42, 1.02, 'Total this day: %02d:%02d h' % (duration_hour, duration_min),
             transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Sunshine.png', dpi=fig_dpi)
    plt.close()

    # Wind Speed 1: col. 24 (10m mean), col. 25 (10m max)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[24].values, color='dodgerblue', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m mean')
    ax.plot(ccurrent.index.values, ccurrent[25].values, color='firebrick', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m max')
    plt.legend(loc='upper right', bbox_to_anchor=(1.25, 1), fontsize=fs_legend)
    plt.ylabel('Wind speed [m/s]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind speed 10 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    ax.set_ylim(bottom=0.)
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Speed.png', dpi=fig_dpi)
    plt.close()

    # Wind Speed 2: col. 27 (2m mean), col. 28 (2m max)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[27].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0, label='Sonic 2m mean')
    ax.plot(ccurrent.index.values, ccurrent[28].values, color='mediumorchid', marker='.',
            markersize=6, linewidth=0, label='Sonic 2m max')
    plt.legend(loc='upper right', bbox_to_anchor=(1.23, 1), fontsize=fs_legend)
    plt.ylabel('Wind speed [m/s]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind speed 2 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    ax.set_ylim(bottom=0.)
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.07, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Speed2.png', dpi=fig_dpi)
    plt.close()

    # Wind Speed mixed: col. 24 (10m mean), col. 27 (2m mean)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[24].values, color='dodgerblue', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m mean')
    ax.plot(ccurrent.index.values, ccurrent[27].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0, label='Sonic 2m mean')
    plt.legend(loc='upper right', bbox_to_anchor=(1.24, 1), fontsize=fs_legend)
    plt.ylabel('Wind speed [m/s]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind speed 2 m and 10 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    ax.set_ylim(bottom=0.)
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.07, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'SpeedC.png', dpi=fig_dpi)
    plt.close()

    # Wind Direction: col. 26 (10m)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[26].values, color='dodgerblue', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m')
    plt.legend(loc='upper right', bbox_to_anchor=(1.18, 1), fontsize=fs_legend)
    plt.ylabel('Wind direction [°]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind direction 10 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    ax.set_ylim([0.,360.])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Direction.png', dpi=fig_dpi)
    plt.close()

    # Wind Direction 2: col. 29 (2m)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[29].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0, label='Sonic 2m')
    plt.legend(loc='upper right', bbox_to_anchor=(1.16, 1), fontsize=fs_legend)
    plt.ylabel('Wind direction [°]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind direction 2 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Direction2.png', dpi=fig_dpi)
    plt.close()

    # Wind direction C: col. 26 (10m), col. 29 (2m)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[26].values, color='dodgerblue', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m')
    ax.plot(ccurrent.index.values, ccurrent[29].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0, label='Sonic 2m')
    plt.legend(loc='upper right', bbox_to_anchor=(1.18, 1), fontsize=fs_legend)
    plt.ylabel('Wind direction [°]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Wind direction 2 m and 10 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.07, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'DirectionC.png', dpi=fig_dpi)
    plt.close()

    #make windrose 10m

    fig = plt.figure(figsize=(13, 6))
    wind10ms = pd.concat([ccurrent[26], ccurrent[24]], axis=1, keys=['wd', 'ws'])    # new df for accurate NaN-removal
    wind10m = wind10ms[wind10ms['wd'].notna() & wind10ms['ws'].notna()]                 # select only non-NaN values
    
    windmax = np.max(wind10ms[wind10ms['wd'].notna() & wind10ms['ws'].notna()]['ws'].values)
    bins = [x/6.*np.ceil(windmax) for x in range(7)]
    ax2 = WindroseAxes.from_ax()
    ax2.bar(wind10m['wd'].values, wind10m['ws'].values, bins=bins,normed=True, opening=0.9, edgecolor='dimgray',
           linewidth=1, cmap=cm.viridis)
    ax2.set_legend(loc='upper right', title='Wind speed [m/s]', borderaxespad=-17., bbox_to_anchor=[0.95, 0.6])
    ax2.set_title('Windrose for Sonic 10 m wind. Period\n'+ccurrent.index[0].strftime('%Y-%m-%d %H:%M:%S-')+ccurrent.index[-1].strftime('%Y-%m-%d %H:%M:%S'), fontsize=fs_title, pad=40)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.1, 1.25), frameon=False, xycoords=ax.transAxes)
    ax2.add_artist(ab)
    plt.savefig(datadir + 'Windrose10m.png', dpi=fig_dpi, bbox_inches='tight', pad_inches=0.8)
    plt.close()

    # Wind rose for 2m wind (wd: col. 29, ws: col. 27)
  
    wind2ms = pd.concat([ccurrent[29], ccurrent[27]], axis=1, keys=['wd', 'ws'])    # new df for accurate NaN-removal
    wind2m = wind2ms[wind2ms['wd'].notna() & wind2ms['ws'].notna()]                 # select only non-NaN values
    fig = plt.figure(figsize=(13, 6))
    
    ax1 = WindroseAxes.from_ax()
    ax1.bar(wind2m['wd'].values, wind2m['ws'].values, bins=bins,normed=True, opening=0.9, edgecolor='dimgray',
           linewidth=1, cmap=cm.viridis)
    ax1.set_legend(loc='upper right', title='Wind speed [m/s]', borderaxespad=-17., bbox_to_anchor=[0.95, 0.6])
    ax1.set_title('Windrose for Sonic 2 m wind. Period: \n'+ccurrent.index[0].strftime('%Y-%m-%d %H:%M:%S-')+ccurrent.index[-1].strftime('%Y-%m-%d %H:%M:%S'), fontsize=fs_title, pad=40)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.1, 1.25), frameon=False, xycoords=ax.transAxes)
    ax1.add_artist(ab)
    plt.savefig(datadir + 'Windrose2m.png', dpi=fig_dpi, bbox_inches='tight', pad_inches=0.8)
    plt.close()

    images = [Image.open(x) for x in [datadir + 'Windrose2m.png',datadir + 'Windrose10m.png']]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,0))
      x_offset += im.size[0]

    new_im.save(datadir+'Windroses_combined.png')

    # Ground water level: col. 30 (gwl)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[30].apply(lambda x: round(x,2)).values, color='firebrick', linewidth=2)
    plt.ylabel('Water level [m below surface]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Ground water level', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_ylim([ccurrent[30].min() - 0.2,ccurrent[30].max() + 0.2]) # changed 20230605 KvdD added .2m to top and substracted from bottom scale
    ax.invert_yaxis()
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Gwl.png', dpi=fig_dpi)
    plt.close()

    # Visibility: col. 18
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[18].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0)
    #ax.plot(ccurrent.index.values, ccurrent[18].values, color='forestgreen', linewidth=2)  #ESG_SB_20230921+ Changed visibility from line to markers because line was not visible at 7999.0 visibility
    plt.ylabel('Visibility [m]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Visibility', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    ax.set_ylim([0.,8000.])

    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'visibility.png', dpi=fig_dpi)
    plt.close()

    # Volumetric water content: col. 45 (6.5cm), col. 46 (12.5cm), col. 47 (25cm), col. 48 (50cm), col. 49 (-6.5cm),
    # col. 50 (-12.5cm), col. 51 (-25cm), col. 52 (-50cm), col. 53 (6.5cm bare)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[45].values, color='deeppink', label='6.5 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[49].values, color='deeppink', label='-6.5 cm (2)', linewidth=2, linestyle='--')
    ax.plot(ccurrent.index.values, ccurrent[46].values, color='darkcyan', label='12.5 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[50].values, color='darkcyan', label='-12.5 cm (2)', linewidth=2, linestyle='--')
    ax.plot(ccurrent.index.values, ccurrent[47].values, color='mediumblue', label='25 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[51].values, color='mediumblue', label='-25 cm (2)', linewidth=2, linestyle='--')
    ax.plot(ccurrent.index.values, ccurrent[48].values, color='firebrick', label='50 cm', linewidth=2)
    ax.plot(ccurrent.index.values, ccurrent[52].values, color='firebrick', label='-50 cm (2)', linewidth=2, linestyle='--')
    ax.plot(ccurrent.index.values, ccurrent[53].values, color='dimgrey', label='6.5 cm bare', linewidth=2, linestyle='-.')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1), fontsize=fs_legend)
    plt.ylabel('Volumetric water content [-]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Volumetric water content', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.06, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'VWC.png', dpi=fig_dpi)
    plt.close()

    # Data text
    humidity = ccurrent[8][-11:].mean()
    pressure = ccurrent[21][-11:].mean()
    ws_10m = ccurrent[24][-11:].mean()
    wd_10m = ccurrent[26][-11:].mean()
    # rain_last24h => rain_sum
    rain_last10min = ccurrent[63-44][-11:].sum()
    gwl = ccurrent[30][-11:].mean()
    rad_glb_in = ccurrent[9][-11:].mean()
    rad_diff = ccurrent[14][-11:].mean()
    rad_net = ccurrent[13][-11:].mean()
    # sun => duration_hour & duration_min
    visib = ccurrent[18][-11:].mean()
    heatfl_grass = ccurrent[42][-11:].mean()
    heatfl_soil = ccurrent[44][-11:].mean()
    # Figure
    fig, ax = plt.subplots(figsize=(13, 6))
    plt.text(0.26, 1.2, 'Date: %s,    Time [UTC]: %s - %s' % (date_text, ccurrent.index[-11].strftime('%H:%M'),
                                                        ccurrent.index[-1].strftime('%H:%M')),
             transform=ax.transAxes, fontsize=15, weight='bold')
    plt.text(0.3, 1.08, 'Average or sum of data of the last 10 minutes', transform=ax.transAxes, fontsize=15)
    # first column
    plt.text(0.07, 0.9, 'Temperature: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.9, '%.1f °C' % tmean_last10min,  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.8, 'Humidity: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.8, '%.1f %%' % humidity,  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.7, 'Pressure: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.7, '%.2f kPa' % pressure,  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.6, 'Wind speed (10m): ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.6, '%.1f $ms^{-1}$' % ws_10m,  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.5, 'Wind direction: ',  transform=ax.transAxes, fontsize=15)
    try:
        plt.text(0.32, 0.5, '%d °' % round(wd_10m),  transform=ax.transAxes, fontsize=15)
    except:
        print('WD10 could not be rounded')
    plt.text(0.07, 0.4, 'Rainfall last 24 hours: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.4, '%.2f mm' % rain_sum[-1],  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.3, 'Rainfall last 10 minutes: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.3, '%.2f mm' % rain_last10min,  transform=ax.transAxes, fontsize=15)
    plt.text(0.07, 0.2, 'Ground water level: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.32, 0.2, '%.2f m' % gwl,  transform=ax.transAxes, fontsize=15)
    # second column
    plt.text(0.57, 0.9, 'Global incoming radiation: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.9, '%d $Wm^{-2}$' % rad_glb_in,  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.8, 'Diffuse radiation: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.8, '%d $Wm^{-2}$' % rad_diff,  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.7, 'Net radiation: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.7, '%d $Wm^{-2}$' % rad_net,  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.6, 'Sunshine total this day: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.6, '%02d:%02d h' % (duration_hour, duration_min),  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.5, 'Visibility: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.5, '%d m' % int(visib),  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.4, 'Heat flux under grass: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.4, '%d $Wm^{-2}$' % round(heatfl_grass),  transform=ax.transAxes, fontsize=15)
    plt.text(0.57, 0.3, 'Heat flux under bare soil: ',  transform=ax.transAxes, fontsize=15)
    plt.text(0.82, 0.3, '%d $Wm^{-2}$' % round(heatfl_soil),  transform=ax.transAxes, fontsize=15)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.1, 1.18), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(datadir + 'Data.png', dpi=fig_dpi)
    plt.close()

    # Cup: col. 22 (w.speed cup 10m), col. 23 (w.speed cup 10m max), col. 24 (w.speed sonic 10m)
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(ccurrent.index.values, ccurrent[22].values, color='mediumorchid', marker='.',
            markersize=6, linewidth=0, label='Cup 10m')
    ax.plot(ccurrent.index.values, ccurrent[23].values, color='dodgerblue', marker='.',
            markersize=6, linewidth=0, label='Cup 10m max')
    ax.plot(ccurrent.index.values, ccurrent[24].values, color='forestgreen', marker='.',
            markersize=6, linewidth=0, label='Sonic 10m')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1), fontsize=fs_legend)
    plt.ylabel('Wind speed [m/s]', fontsize=fs_labels)
    plt.xlabel('Time [UTC]', fontsize=fs_labels)
    plt.title('Cup wind speed 10 m', fontsize=fs_title, pad=30)
    plt.grid(color='gainsboro', linestyle='--', which='both')
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n %d %b %Y'))
    ax.set_xlim([xlim, ccurrent.index[-1]])
    for item in (ax.get_xticklabels(which='both') + ax.get_yticklabels()):
        item.set_fontsize(fs_ticks)
    plt.text(0.8, 1.05, date_text, transform=ax.transAxes, fontsize=fs_text)
    imagebox = OffsetImage(logo, zoom=0.5)
    ab = AnnotationBbox(imagebox, (0.07, 1.12), frameon=False, xycoords=ax.transAxes)
    ax.add_artist(ab)
    plt.tight_layout()
    plt.savefig(datadir + 'Cup.png', dpi=fig_dpi)
    plt.close()
