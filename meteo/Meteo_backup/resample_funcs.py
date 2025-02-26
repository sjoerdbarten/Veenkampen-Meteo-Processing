import numpy as np

def mean(values):
    if np.isnan(values).any():
        return np.nan
    else:
        return np.mean(values)

def max(values):
    if np.isnan(values).any():
        return np.nan
    else:
        return np.max(values)

def min(values):
    if np.isnan(values).any():
        return np.nan
    else:
        return np.min(values)

def sum(values):
    if np.isnan(values).any():
        return np.nan
    else:
        return np.sum(values)

def calc_angles(angles):

    if np.isnan(angles).any():
        return np.nan
    else:
       sum_s = np.sum(np.sin(angles*np.pi/180.))
       sum_c = np.sum(np.cos(angles*np.pi/180.))
   
       angle = np.arctan2(sum_s, sum_c) * 180. / np.pi
       if angle < 0:
          angle = angle + 360
       return angle


# Calculate positive mean
def pos_mean(values):

    if np.isnan(values).any():
        return np.nan
    else:
      posit_mean = np.nanmean(values.where(values > 0., 0.))
      return posit_mean