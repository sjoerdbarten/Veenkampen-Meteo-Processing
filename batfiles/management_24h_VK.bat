rem if exist C:\Veenkampen\Data\ECraw_VK_prev.dat c:\veenkampen_data\ch\mv C:\Veenkampen\Data\ECraw_VK_prev.dat C:\Veenkampen\Data\ECraw_VK_prev2.dat

rem copy C:\Veenkampen\Data\ECraw_VK.dat W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\raw_data\EC\EC_CR1000\ECraw_VK_prev.dat
rem c:\veenkampen_data\ch\mv C:\Veenkampen\Data\ECraw_VK.dat C:\Veenkampen\Data\ECraw_VK_prev.dat

rem if exist C:\Veenkampen\Data\ECraw_VK_prev2.dat copy C:\Veenkampen\Data\ECraw_VK_prev2.dat W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\raw_data\EC\EC_CR1000\ECraw_VK_%1_%2_%3.dat

rem "c:\program files\7-zip\7z.exe" a C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\ECraw_VK_%1%2%3.7z C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\raw_data_%1_%2_%3_*.dat
rem c:\veenkampen_data\ch\mv C:\Veenkampen\Data\Baler\Data\CR1000_EC\raw_data_%1_%2_%3_*.dat C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\

rem "C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
rem      "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22 -hostkey=""ssh-rsa 4096 dGoG9vfrjgogdgG65ZNLK/dHygmqJxq+JCZm/1AbTwU=""" ^
rem      "cd www/flux/%1/" ^
rem      "put C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\ECraw_VK_%1%2%3.7z" ^
rem      "exit"

rem copy de 
rem copy C:\Veenkampen\Data\Baler\Data\CR1000_EC\Store\ECraw_VK_%1%2%3.7z W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\raw_data\EC\Baler\
rem if exist W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\baler\ECraw_AAMS_%1%2%3.7z del W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\AAMS\baler\raw_data_%1_%2_%3_*.dat
 