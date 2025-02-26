rem store data to WUR server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/data" ^
     "put C:\Veenkampen_Data\C_current.txt" ^
     "put C:\Veenkampen_Data\currentn.txt" ^
     "put C:\Veenkampen_Data\currents.txt" ^
     "put C:\Veenkampen_Data\flux\metgeg.txt" ^
     "exit"

rem store data to Transip server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22 -hostkey=""ssh-rsa 4096 dGoG9vfrjgogdgG65ZNLK/dHygmqJxq+JCZm/1AbTwU=""" ^
     "cd www/data" ^
     "put C:\Veenkampen_Data\C_current.txt" ^
     "put C:\Veenkampen_Data\currentn.txt" ^
     "put C:\Veenkampen_Data\currents.txt" ^
     "put C:\Veenkampen_Data\flux\metgeg.txt" ^
     "cd ../loggerfiles/" ^
     "put C:\Veenkampen\Data\VeenkampenNorth_stats.dat" ^
     "put C:\Veenkampen\Data\VeenkampenSouth_stats.dat" ^
     "exit"

 



