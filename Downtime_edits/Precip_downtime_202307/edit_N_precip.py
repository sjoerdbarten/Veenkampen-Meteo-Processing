import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt

df = pd.read_csv('C_20230727_orig.txt',header=None)
df.iloc[:,19] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('C_20230727_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('C_20230728_orig.txt',header=None)
df.iloc[:,19] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('C_20230728_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('C_20230729_orig.txt',header=None)
df.iloc[:,19] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('C_20230729_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('C_20230730_orig.txt',header=None)
df.iloc[:,19] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('C_20230730_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('C_20230731_orig.txt',header=None)
df.iloc[:,19] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('C_20230731_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('N20230727_orig.txt',header=None)
df.iloc[:,22] = -999
df.iloc[:,-1] = -999
df.iloc[:,-2] = -999
df.iloc[:,-3] = -999
df.iloc[:,-4] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('N20230727_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('N20230728_orig.txt',header=None)
df.iloc[:,22] = -999
df.iloc[:,-1] = -999
df.iloc[:,-2] = -999
df.iloc[:,-3] = -999
df.iloc[:,-4] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('N20230728_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('N20230729_orig.txt',header=None)
df.iloc[:,22] = -999
df.iloc[:,-1] = -999
df.iloc[:,-2] = -999
df.iloc[:,-3] = -999
df.iloc[:,-4] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('N20230729_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('N20230730_orig.txt',header=None)
df.iloc[:,22] = -999
df.iloc[:,-1] = -999
df.iloc[:,-2] = -999
df.iloc[:,-3] = -999
df.iloc[:,-4] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('N20230730_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

df = pd.read_csv('N20230731_orig.txt',header=None)
df.iloc[:,22] = -999
df.iloc[:,-1] = -999
df.iloc[:,-2] = -999
df.iloc[:,-3] = -999
df.iloc[:,-4] = -999
df.iloc[:,0] = df.iloc[:,0].astype(str)
df.to_csv('N20230731_new.txt', header=False, index=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
