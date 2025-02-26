import sys
import os
import shutil
import datetime
from dirsync import sync
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                ziph.write(os.path.join(root, file))
            except PermissionError as e:
                continue

def IsPathValid(path, ignoreDir, ignoreExt):
    splited = None
    if os.path.isfile(path):
        if ignoreExt:
            _, ext = os.path.splitext(path)
            if ext in ignoreExt:
                return False

        splited = os.path.dirname(path).split('\\/')
    else:
        if not ignoreDir:
            return True
        splited = path.split('\\/')

    if ignoreDir:
        for s in splited:
            if s in ignoreDir:  # You can also use set.intersection or [x for],
                return False

    return True


def zipDirHelper(path, rootDir, zf, ignoreDir=None, ignoreExt=None):
    # zf is zipfile handle
    if os.path.isfile(path):
        if IsPathValid(path, ignoreDir, ignoreExt):
            relative = os.path.relpath(path, rootDir)
            #zipdir(path, zf)
            zf.write(path, relative)
        return

    ls = os.listdir(path)
    for subFileOrDir in ls:
        if not IsPathValid(subFileOrDir, ignoreDir, ignoreExt):
            continue

        joinedPath = os.path.join(path, subFileOrDir)
        zipDirHelper(joinedPath, rootDir, zf, ignoreDir, ignoreExt)


def ZipDir(path, zf, ignoreDir=None, ignoreExt=None, close=False):
    rootDir = path if os.path.isdir(path) else os.path.dirname(path)

    try:
        zipDirHelper(path, rootDir, zf, ignoreDir, ignoreExt)
    finally:
        if close:
            zf.close()

c_path = "C:"
m_path = "M:"
w_path = 'W:\ESG\DOW_MAQ\MAQ_Archive\Veenkampen_archive\Backups'

today = datetime.datetime.today().strftime('%Y%m%d')
newpath = os.path.join(w_path,"L0153962_"+str(today))
newpath_m = os.path.join(m_path,"backup_temp_L0153962")

if not os.path.exists(newpath):
    print('Making new directory on W:\ archive')
    print(newpath)
    os.makedirs(newpath)
if not os.path.exists(newpath_m):
    print('Making new temporary directory on M:\ archive')
    print(newpath_m)
    os.makedirs(newpath_m)

print('Making temporary .zip archives')
zipf = zipfile.ZipFile(os.path.join(newpath_m,"AAMS.zip"), 'w', zipfile.ZIP_DEFLATED)
ZipDir(os.path.join(c_path,"\\AAMS"), zipf, ignoreDir=["CR_muntplein","output"], close=True)
zipf.close()

zipf = zipfile.ZipFile(os.path.join(newpath_m,"Veenkampen.zip"), 'w', zipfile.ZIP_DEFLATED)
ZipDir(os.path.join(c_path,"\\Veenkampen"), zipf, ignoreDir=["Data","output"], close=True)
zipf.close()

zipf = zipfile.ZipFile(os.path.join(newpath_m,"Veenkampen_install.zip"), 'w', zipfile.ZIP_DEFLATED)
ZipDir(os.path.join(c_path,"\\Veenkampen_install"), zipf, close=True)
zipf.close()

zipf = zipfile.ZipFile(os.path.join(newpath_m,"scintis.zip"), 'w', zipfile.ZIP_DEFLATED)
ZipDir(os.path.join(c_path,"\\scintis"), zipf, close=True)
zipf.close()


print('Synchronizing .zip archives from M:/ to W:/ drive')
sync(os.path.join(m_path,"backup_temp_L0153962"), os.path.join(newpath), 'sync')

print('Removing temporary .zip archives from M:/')
os.remove(os.path.join(newpath_m,"AAMS.zip"))
os.remove(os.path.join(newpath_m,"Veenkampen.zip"))
os.remove(os.path.join(newpath_m,"Veenkampen_install.zip"))
os.remove(os.path.join(newpath_m,"scintis.zip"))
