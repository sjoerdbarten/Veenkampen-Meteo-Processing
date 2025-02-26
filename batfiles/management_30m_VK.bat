rem %1=current hour  %2= previous hour %3= prev prev hour %4= "00" %5=yyyy-mm-dd


IF %4% GEQ 37 (
  set VAR1=30
  set VAR2=38
  set VAR3=39
)else (
  set VAR1=00
  set VAR2=08
  set VAR3=09
)


rem C:\Veenkampen_Data\ch\mv C:\Veenkampen\Data\Baler\Data\CR1000_EC\raw_data_*_%3%VAR1%.dat C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\

rem copy C:\AAMS\CR_muntplein_raw_data.dat W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\raw_data\

 IF exist C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\eddypro_VK_full*T%1%VAR2%*.csv (
  
   C:\Veenkampen_Data\ch\tail -q --lines=1 C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\eddypro_VK_full*T%1%VAR2%*.csv > C:\Veenkampen_Data\flux\flux_VK_line.txt
 ) ELSE IF exist C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\eddypro_VK_full*T%1%VAR3%*.csv (
   C:\Veenkampen_Data\ch\tail -q --lines=1 C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\eddypro_VK_full*T%1%VAR3%*.csv > C:\Veenkampen_Data\flux\flux_VK_line.txt
 ) ELSE (
   echo 'not there'
   echo file_not_exist,%5,%1:%VAR1%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,, > C:\Veenkampen_Data\flux\NoData_VK.txt
   set ToCopyFile=C:\Veenkampen_Data\flux\NoData_VK.txt
 )
 
 if exist C:\Veenkampen_Data\flux\flux_VK_line.txt set ToCopyFile=C:\Veenkampen_Data\flux\flux_VK_line.txt
 copy %ToCopyFile%  C:\Veenkampen_Data\flux\correct_VK_line.txt

 C:\Veenkampen_Data\ch\type C:\Veenkampen_Data\flux\correct_VK_line.txt >> C:\Veenkampen_Data\flux\flux_VK.log

 C:\Veenkampen_Data\ch\type C:\Veenkampen_Data\flux\correct_VK_line.txt >> C:\Veenkampen_Data\flux\Eddyflux.csv
 C:\Veenkampen_Data\ch\tail --lines=48 C:\Veenkampen_Data\flux\Eddyflux.csv > C:\Veenkampen_Data\flux\eddyflux24h.txt

rem copy C:\AAMS\flux\Eddyflux_AAMS.csv W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\raw_data\EC\
rem copy  C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\AAMS\*.csv W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\raw_data\EC\datfiles\
C:\Veenkampen_Data\ch\mv C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\*.csv C:\Veenkampen\EddyPro_batch_v7\EddyPro-7.0.6\output\eddypro_stats\

 del C:\Veenkampen_Data\flux\flux_VK_line.txt
