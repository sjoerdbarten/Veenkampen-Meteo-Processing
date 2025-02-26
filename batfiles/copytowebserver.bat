
"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/data/%1/%2" ^
     "put C:\Veenkampen_Data\%1\%2\C_%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\10min_%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\N%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\S%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\M_%1%2.txt" ^
     "put C:\Veenkampen_Data\%1\%2\hour_%1%2%3.txt" ^
     "exit"

rem store data to Transip server

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22 -hostkey=""ssh-rsa 4096 dGoG9vfrjgogdgG65ZNLK/dHygmqJxq+JCZm/1AbTwU=""" ^
     "cd www/data/%1/%2" ^
     "put C:\Veenkampen_Data\%1\%2\C_%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\10min_%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\N%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\S%1%2%3.txt" ^
     "put C:\Veenkampen_Data\%1\%2\M_%1%2.txt" ^
     "put C:\Veenkampen_Data\%1\%2\hour_%1%2%3.txt" ^
     "exit"
