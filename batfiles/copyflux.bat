rem copy to met.wur.nl server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/data/%1/%2" ^
     "put C:\Veenkampen_Data\flux\eddyflux24h.txt flux_%1%2%3.txt" ^
     "exit"

rem store data to Transip server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22 -hostkey=""ssh-rsa 4096 dGoG9vfrjgogdgG65ZNLK/dHygmqJxq+JCZm/1AbTwU=""" ^
     "cd www/data/%1/%2" ^
     "put C:\Veenkampen_Data\flux\eddyflux24h.txt flux_%1%2%3.txt" ^
     "exit"

rem produce flux graphs of previous day on met.wur.nl server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/graphs/%4" ^
     "put c:\Veenkampen_Data\graphs\Flux.png" ^
     "put c:\Veenkampen_Data\graphs\CO2.png" ^
     "put c:\Veenkampen_Data\graphs\CO2-conc.png" ^
     "exit"