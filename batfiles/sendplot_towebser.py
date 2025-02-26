import pysftp as sftp

cnopts = sftp.CnOpts()
cnopts.hostkeys = None          


srv = sftp.Connection(host="veenka.ssh.transip.me",username="veenkampennl",password="MAQ_transip_2023",cnopts=cnopts)
srv.cwd('/www/data/')
srv.makedirs("BC_exp/"+dt.strftime('%Y/%m'), mode=777)  # will happily make all non-existing directories
srv.cwd("/www/graphs/cur/")
print(srv.pwd)
srv.put('C:\veenkampen_data\graphs\cur\*png')
srv.close()