"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open ftp://metwurnl:Maq_12345@server201.da.bizway.nl:21" ^
     "cd domains/met.wur.nl/public_html/AAMS/graphs/%1" ^
     "put  c:\AAMS\fluxes\graphs\cur\*.png" ^
      "exit"