echo "Starts Excel Grahp_2.xlsm in xx seconds"
timeout /t 5
start "graphstart" "C:\Program Files (x86)\Microsoft Office\root\Office16\Excel.exe" /x c:\veenkampen\graph.xlsm

exit