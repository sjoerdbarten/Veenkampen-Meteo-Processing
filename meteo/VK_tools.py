import pandas as pd
import numpy as np
import ssl


#
# the C_current.txt, the 10minute_current.txt,uurdata.txt requires specific formatting
# in this function values of 0.0 are set to 0.
# while other values rounding is done on three decimals while the tailing 0's
# to the right are removed 
#

def formatting(value):
   dmod = value % 1
   if (dmod == 0.0): 
      return('%.f.' % value)
   else:
      out = '%.3f' % value
      return(out.rstrip('0'))

#
# Get data of last 24 hours from Veenkampen website
#
# two file are being read
# 1) veenkampen<logger_stats_prevmont.dat : data from previous month
# 2) veenkampen<Logger>_stats.dat : current month 
#

def get_data24h(file_name_in, startd, stopd):
    ssl._create_default_https_context = ssl._create_unverified_context

# reading of data from previous month as pandas dataframe
#    
    file_name = file_name_in+'_prevmonth.dat'
    fg_prevmonth = pd.read_csv(file_name, header=None, skiprows=4, sep=',', parse_dates=True,
                     index_col=0, na_values='NAN', dtype='float')
    
#
# redading of data from current month
#
 
    file_name = file_name_in+'.dat'
    fg_act = pd.read_csv(file_name, header=None, skiprows=4, sep=',', parse_dates=True,
                     index_col=0, na_values='NAN', dtype='float')   
   
# 
# concatenation of data from previous and current month
#

    fg = pd.concat([fg_prevmonth,fg_act],axis=0)

#
# getting data of last 24 hours
#
    last10minute = fg.loc[(fg.index >= startd) & (fg.index <= stopd)]

#
# re-indexing to one-minute files (handling of missing lines as lines where the all data are set to -999.
#
    last10minute = last10minute[~last10minute.index.duplicated()]
    last10minute = last10minute.reindex(pd.date_range(startd, stopd, freq='min'))
    last10minute = last10minute.fillna(-999.)

    return last10minute


# Define a table so that all variables are properly read, processed and written away
def get_table():
    # ic = np.zeros((63, 6), dtype=np.int8)
    ic = np.zeros((62, 5), dtype=np.int8)
    name = []
    # north (=1)             input column            calculation               pos in output_10min,  pos in out_1minute    name of the variable          
    # or south (=2)          position of             - 1: only mean                 output_hourly,
    #                        variable in             - 2: mean, max                 output_day.
    #                        input files             - 3: mean,max,min
    #                                                - 4: sum
    #                                                - 5: angle
    #                                                - 6: positive mean
    #                                                - 7: max
    #                                                - 9: missing
    #                                                -10: no output value
    #                                                     /do nothing

    ic[0, 0] = 1;           ic[0, 1] = 19;          ic[0, 2] = 3;           ic[0, 3] = 7;           ic[0, 4] = 3;         name.append('Temp unventilated dry') #        1
    ic[1, 0] = 1;           ic[1, 1] = 20;          ic[1, 2] = 3;           ic[1, 3] = 10;          ic[1, 4] = 4;         name.append('Temp unventilated wet') #        2
    ic[2, 0] = 2;           ic[2, 1] = 20;          ic[2, 2] = 3;           ic[2, 3] = 1;           ic[2, 4] = 1;         name.append('Temp ventilated dry')   #        3
    ic[3, 0] = 2;           ic[3, 1] = 21;          ic[3, 2] = 3;           ic[3, 3] = 4;           ic[3, 4] = 2;         name.append('Temp ventilated wet')    #        4
    ic[4, 0] = 2;           ic[4, 1] = 19;          ic[4, 2] = 3;           ic[4, 3] = 13;          ic[4, 4] = 5;         name.append('T+10cm shielded')       #        5
    ic[5, 0] = 1;           ic[5, 1] = 17;          ic[5, 2] = 1;           ic[5, 3] = 16;          ic[5, 4] = 6;         name.append('T vaisala')             #        6
    ic[6, 0] = 1;           ic[6, 1] = 18;          ic[6, 2] = 1;           ic[6, 3] = 17;          ic[6, 4] = 7;         name.append('Humidity')              #        7
    ic[7, 0] = 2;           ic[7, 1] = 3;           ic[7, 2] = 6;           ic[7, 3] = 18;          ic[7, 4] = 8;         name.append('Qglb in')               #        8
    ic[8, 0] = 2;           ic[8, 1] = 4;           ic[8, 2] = 6;           ic[8, 3] = 19;          ic[8, 4] = 9;         name.append('Qglb out')              #        9
    ic[9, 0] = 2;           ic[9, 1] = 58;          ic[9, 2] = 1;           ic[9, 3] = 20;          ic[9, 4] = 10;        name.append('QL in')                 #       10
    ic[10, 0] = 2;          ic[10, 1] = 59;         ic[10, 2] = 1;          ic[10, 3] = 21;         ic[10, 4] = 11;       name.append('QL out')                #       11
    ic[11, 0] = 2;          ic[11, 1] = 61;         ic[11, 2] = 1;          ic[11, 3] = 22;         ic[11, 4] = 12;       name.append('Qnet') # recalculc 9-10+11-12   12
    ic[12, 0] = 2;          ic[12, 1] = 10;         ic[12, 2] = 6;          ic[12, 3] = 23;         ic[12, 4] = 13;       name.append('Q diffuse Tracker') #           13
    ic[13, 0] = 2;          ic[13, 1] = 9;          ic[13, 2] = 6;          ic[13, 3] = 24;         ic[13, 4] = 14;       name.append('Q beam Tracker') #              14
    ic[14, 0] = 2;          ic[14, 1] = 60;         ic[14, 2] = 1;          ic[14, 3] = 25;         ic[14, 4] = 15;       name.append('Q long in Tracker') #           15
    ic[15, 0] = 2;          ic[15, 1] = 13;         ic[15, 2] = 4;          ic[15, 3] = 26;         ic[15, 4] = 16;       name.append('Sunshine') #                    16
    ic[16, 0] = 2;          ic[16, 1] = 15;         ic[16, 2] = 1;          ic[16, 3] = 27;         ic[16, 4] = 17;       name.append('Visibility') #                  17
    # changed input for precipitation from 23 to 33 Accumulated RT-NRT
    ic[17, 0] = 1;          ic[17, 1] = 33;         ic[17, 2] = 4;          ic[17, 3] = 28;         ic[17, 4] = 18;       name.append('Precipitation') #               18
    ic[18, 0] = 1;          ic[18, 1] = 15;         ic[18, 2] = 2;          ic[18, 3] = 29;         ic[18, 4] = 19;       name.append('snow height') #                 19
    ic[19, 0] = 1;          ic[19, 1] = 27;         ic[19, 2] = 1;          ic[19, 3] = 31;         ic[19, 4] = 20;       name.append('Pressure') #                    20
    ic[20, 0] = 1;          ic[20, 1] = 21;         ic[20, 2] = 1;          ic[20, 3] = 32;         ic[20, 4] = 21;       name.append('windspeed 10 m cup') #          21
    ic[21, 0] = 1;          ic[21, 1] = 26;         ic[21, 2] = 7;          ic[21, 3] = 33;         ic[21, 4] = 22;       name.append('windspeed 10 m cup max') #      22
    ic[22, 0] = 1;          ic[22, 1] = 3;          ic[22, 2] = 1;          ic[22, 3] = 34;         ic[22, 4] = 23;       name.append('windspeed 10 m sonic') #        23
    ic[23, 0] = 1;          ic[23, 1] = 7;          ic[23, 2] = 7;          ic[23, 3] = 35;         ic[23, 4] = 24;       name.append('windspeed 10 m sonic  max') #   24
    ic[24, 0] = 1;          ic[24, 1] = 4;          ic[24, 2] = 5;          ic[24, 3] = 36;         ic[24, 4] = 25;       name.append('wind direction 10 m sonic') #   25
    ic[25, 0] = 1;          ic[25, 1] = 9;          ic[25, 2] = 1;          ic[25, 3] = 37;         ic[25, 4] = 26;       name.append('windspeed 2m') #                26
    ic[26, 0] = 1;          ic[26, 1] = 13;         ic[26, 2] = 7;          ic[26, 3] = 38;         ic[26, 4] = 27;       name.append('windspeed 2m max') #            27
    ic[27, 0] = 1;          ic[27, 1] = 10;         ic[27, 2] = 5;          ic[27, 3] = 39;         ic[27, 4] = 28;       name.append('wind 2m direction') #           28
    ic[28, 0] = 2;          ic[28, 1] = 36;         ic[28, 2] = 1;          ic[28, 3] = 40;         ic[28, 4] = 29;       name.append('Groundwaterlevel') #             29
    ic[29, 0] = 2;          ic[29, 1] = 22;         ic[29, 2] = 3;          ic[29, 3] = 41;         ic[29, 4] = 30;       name.append('Tgras   05cm') #                30
    ic[30, 0] = 2;          ic[30, 1] = 23;         ic[30, 2] = 3;          ic[30, 3] = 44;         ic[30, 4] = 31;       name.append('Tgras   10cm') #                31
    ic[31, 0] = 2;          ic[31, 1] = 24;         ic[31, 2] = 3;          ic[31, 3] = 47;         ic[31, 4] = 32;       name.append('Tgras   20cm') #                32
    ic[32, 0] = 2;          ic[32, 1] = 25;         ic[32, 2] = 3;          ic[32, 3] = 50;         ic[32, 4] = 33;       name.append('Tgras   50cm') #                33
    ic[33, 0] = 2;          ic[33, 1] = 26;         ic[33, 2] = 1;          ic[33, 3] = 53;         ic[33, 4] = 34;       name.append('Tgras  100cm') #                34
    ic[34, 0] = 2;          ic[34, 1] = 27;         ic[34, 2] = 1;          ic[34, 3] = 54;         ic[34, 4] = 35;       name.append('Tgras  150cm') #                35
    ic[35, 0] = 2;          ic[35, 1] = 28;         ic[35, 2] = 3;          ic[35, 3] = 55;         ic[35, 4] = 36;       name.append('Tbare  05 cm') #                36
    ic[36, 0] = 2;          ic[36, 1] = 29;         ic[36, 2] = 3;          ic[36, 3] = 58;         ic[36, 4] = 37;       name.append('Tbare  10 cm') #                37
    ic[37, 0] = 2;          ic[37, 1] = 30;         ic[37, 2] = 3;          ic[37, 3] = 61;         ic[37, 4] = 38;       name.append('Tbare  20 cm') #                38
    ic[38, 0] = 2;          ic[38, 1] = 31;         ic[38, 2] = 3;          ic[38, 3] = 64;         ic[38, 4] = 39;       name.append('Tbare  50 cm') #                39
    ic[39, 0] = 2;          ic[39, 1] = 33;         ic[39, 2] = 1;          ic[39, 3] = 67;         ic[39, 4] = 40;       name.append('Heat flux 6cm a grass') #       40
    ic[40, 0] = 2;          ic[40, 1] = 34;         ic[40, 2] = 1;          ic[40, 3] = 68;         ic[40, 4] = 41;       name.append('Heat flux 6cm b grass') #       41
    ic[41, 0] = 2;          ic[41, 1] = 35;         ic[41, 2] = 1;          ic[41, 3] = 69;         ic[41, 4] = 42;       name.append('Heat flux 6cm c grass') #       42
    ic[42, 0] = 2;          ic[42, 1] = 32;         ic[42, 2] = 1;          ic[42, 3] = 70;         ic[42, 4] = 43;       name.append('Heat flux 6cm bare') #          43
    ic[43, 0] = 2;          ic[43, 1] = 46;         ic[43, 2] = 1;          ic[43, 3] = 71;         ic[43, 4] = 44;       name.append('VWC 65') #                      44
    ic[44, 0] = 2;          ic[44, 1] = 47;         ic[44, 2] = 1;          ic[44, 3] = 72;         ic[44, 4] = 45;       name.append('VWC 125') #                     45
    ic[45, 0] = 2;          ic[45, 1] = 48;         ic[45, 2] = 1;          ic[45, 3] = 73;         ic[45, 4] = 46;       name.append('VWC 250') #                     46
    ic[46, 0] = 2;          ic[46, 1] = 49;         ic[46, 2] = 1;          ic[46, 3] = 74;         ic[46, 4] = 47;       name.append('VWC 500') #                     47
    ic[47, 0] = 2;          ic[47, 1] = 50;         ic[47, 2] = 1;          ic[47, 3] = 75;         ic[47, 4] = 48;       name.append('VWC 65_2') #                      48
    ic[48, 0] = 2;          ic[48, 1] = 51;         ic[48, 2] = 1;          ic[48, 3] = 76;         ic[48, 4] = 49;       name.append('VWC 125_2') #                     49
    ic[49, 0] = 2;          ic[49, 1] = 52;         ic[49, 2] = 1;          ic[49, 3] = 77;         ic[49, 4] = 50;       name.append('VWC 250_2') #                     50
    ic[50, 0] = 2;          ic[50, 1] = 53;         ic[50, 2] = 1;          ic[50, 3] = 78;         ic[50, 4] = 51;       name.append('VWC 500_2') #                     51
    ic[51, 0] = 2;          ic[51, 1] = 54;         ic[51, 2] = 1;          ic[51, 3] = 79;         ic[51, 4] = 52;       name.append('VWC 55 bare') #                 52
    # by setting the calculation to 10 nothing is done and the data is filled by the tipping bucket ic[18,1]=23
    ic[52, 0] = 1;          ic[52, 1] = 28;         ic[52, 2] = 10;         ic[52, 3] = 28;         ic[52, 4] = 18;       name.append('Rain level mean ') #            53
    # ic[18, 1] = 1;          ic[18, 2] = 23;         ic[18, 3] = 4;          ic[18, 4] = 28;         ic[18, 5] = 18;     name.append('Precipitation') #               18
    # ic[53, 1] = 1;          ic[53, 2] = 28;         ic[53, 3] = 4;          ic[53, 4] = 28;         ic[53, 5] = 18;     name.append('Rain level mean_2') #           53
    ic[53, 0] = 1;          ic[53, 1] = 29;         ic[53, 2] = 10;         ic[53, 3] = 99;         ic[53, 4] = 99;       name.append('Rain level max') #              54
    ic[54, 0] = 1;          ic[54, 1] = 30;         ic[54, 2] = 10;         ic[54, 3] = 99;         ic[54, 4] = 99;       name.append('Rain level min') #              55
    ic[55, 0] = 1;          ic[55, 1] = 31;         ic[55, 2] = 1;          ic[55, 3] = 81;         ic[55, 4] = 54;       name.append('Rain duration') #               56
    # new rain sensor
    ic[56, 0] = 1;          ic[56, 1] = 32;         ic[56, 2] = 4;          ic[56, 3] = 82;         ic[56, 4] = 55;       name.append('Rain level mean_3') #           53
    ic[57, 0] = 1;          ic[57, 1] = 33;         ic[57, 2] = 4;          ic[57, 3] = 83;         ic[57, 4] = 56;       name.append('Rain level mean_4') #           53
    ic[58, 0] = 1;          ic[58, 1] = 34;         ic[58, 2] = 4;          ic[58, 3] = 84;         ic[58, 4] = 57;       name.append('Rain level mean_5') #           53
    ic[59, 0] = 1;          ic[59, 1] = 35;         ic[59, 2] = 7;          ic[59, 3] = 85;         ic[59, 4] = 58;       name.append('Rain level mean_6') #           53
    ic[60, 0] = 1;          ic[60, 1] = 36;         ic[60, 2] = 7;          ic[60, 3] = 86;         ic[60, 4] = 59;       name.append('Rain level mean_7') #           53
    ic[61, 0] = 1;          ic[61, 1] = 37;         ic[61, 2] = 7;          ic[61, 3] = 87;         ic[61, 4] = 60;       name.append('Rain level mean_8') #           53

    # rearrange variables
    ic[:, 1] = ic[:, 1] - 1  # python arrays start with 0 (and not 1)
    ic[:, 3] = ic[:, 3] + 1  # shift all columns to the right so that first two columns are date and time respectively
    ic[:, 4] = ic[:, 4] + 1  # shift all columns to the right so that first two columns are date and time respectively

    # get a list of all variables that gathered by the north datalogger
    northlist = [xx for xx in zip(ic[:, 0], ic[:, 1], ic[:, 2], ic[:, 3], ic[:, 4]) if xx[0] == 1 and xx[4] < 90]
    northlist_dict = {name[iter]:xx for iter,xx in enumerate(zip(ic[:, 0], ic[:, 1], ic[:, 2], ic[:, 3], ic[:, 4])) if xx[0] == 1 and xx[4] < 90}

    # get a list of all variables that are gathered at the south datalogger
    southlist = [xx for xx in zip(ic[:, 0], ic[:, 1], ic[:, 2], ic[:, 3], ic[:, 4]) if xx[0] == 2 and xx[4] < 90]
    southlist_dict = {name[iter]:xx for iter,xx in enumerate(zip(ic[:, 0], ic[:, 1], ic[:, 2], ic[:, 3], ic[:, 4])) if xx[0] == 2 and xx[4] < 90}
    return [northlist_dict,southlist_dict]