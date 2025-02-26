"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/graphs/%4" ^
     "put c:\Veenkampen_Data\graphs\*.png" ^
     "exit"

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22 -hostkey=""ssh-rsa 4096 dGoG9vfrjgogdgG65ZNLK/dHygmqJxq+JCZm/1AbTwU=""" ^
     "cd www/graphs/%4" ^
     "put c:\Veenkampen_Data\graphs\*.png" ^
     "exit"
