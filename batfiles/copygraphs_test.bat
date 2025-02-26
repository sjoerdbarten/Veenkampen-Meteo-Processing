"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/veenkampen/graphs/cur" ^
     "put  c:\Veenkampen_Data\graphs\*.png" ^
     "cd domains/met.wur.nl/public_html/veenkampen/graphs/cur/ResizedImages" ^
     "put c:\Veenkampen_Data\graphs\*.png" ^
      "exit"

"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampen.nl:MAQ_transip_2021@veenkampen.nl.transurl.nl:22" ^
     "cd www/graphs/cur" ^
     "put  c:\Veenkampen_Data\graphs\*.png" ^
     "cd www/graphs/cur/ResizedImages" ^
     "put c:\Veenkampen_Data\graphs\*.png" ^
      "exit"
