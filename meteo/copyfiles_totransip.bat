"C:\Program Files (x86)\WinSCP\winscp.com" /ini=nul /command ^
     "open sftp://veenkampennl:MAQ_transip_2023@veenka.ssh.transip.me ""-hostkey=ssh-ed25519 255 /futUoWIBNvvmkbTbwlNIoQ3sq20AfJtvteHCYtUTrc=" ^
     "cd www/data" ^
     "put c:\veenkampen_data\C_current.txt" ^
     "put c:\veenkampen_data\currents.txt" ^
     "put c:\veenkampen_data\currentn.txt" ^
     "put c:\veenkampen_data\10min_current.txt" ^
     "put c:\veenkampen_data\uurdata.txt" ^
     "put c:\veenkampen_data\flux\metgeg.txt" ^
      "exit"