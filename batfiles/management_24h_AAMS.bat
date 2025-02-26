if exist c:\AAMS\ECraw_AAMS_prev.dat c:\veenkampen_data\ch\mv c:\AAMS\ECraw_AAMS_prev.dat c:\AAMS\ECraw_AAMS_prev2.dat

copy c:\AAMS\CR_muntplein_raw_data.dat W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\raw_data\ECraw_AAMS_prev.dat
c:\veenkampen_data\ch\mv c:\AAMS\CR_muntplein_raw_data.dat c:\AAMS\ECraw_AAMS_prev.dat

if exist c:\AAMS\ECraw_AAMS_prev2.dat copy c:\AAMS\ECraw_AAMS_prev2.dat W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\raw_data\ECraw_AAMS_%1_%2_%3.dat

"c:\program files\7-zip\7z.exe" a C:\AAMS\CR_muntplein\ECraw_AAMS_%1%2%3.7z C:\AAMS\CR_muntplein\store\raw_data_%1_%2_%3_*.dat
rem del C:\AAMS\CR_muntplein\store\raw_data_%1_%2_%3_*.dat

rem copy de 
copy C:\AAMS\CR_muntplein\ECraw_AAMS_%1%2%3.7z W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\baler\
if exist W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\baler\ECraw_AAMS_%1%2%3.7z del W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\baler\raw_data_%1_%2_%3_*.dat
