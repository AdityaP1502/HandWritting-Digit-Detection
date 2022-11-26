import numpy as np
def sortObjs(objs):
    partitions = getPartitions(objs)
    for partition in partitions:
        partition.sort(key = lambda x: x[0][1]) # sort based on min j
    
    return partitions

def fromPixelsToHistogram(img):
    id = np.array([i for i in range(0, 256)])
    x = np.array([0 for i in range(0, 256)])
    
    shape = np.shape(img)
    assert len(shape) == 1, "Image must be serial"
    
    Y = img

    for pix_val in Y:
      x[pix_val] += 1     
    window = 21
    order = 2
    
    from scipy.signal import savgol_filter
    x_smoothen = savgol_filter(x, window, order)
    x_smoothen[x_smoothen<0] = 0
    x_smoothen /= len(Y)
    return np.round(x_smoothen, 5)

def findPeak(x):
  # just find the maximum value between 0 - 200
  peak = [0, 0]
  for i in range(200):
    if peak[1] < x[i]:
      peak = [i, x[i]]

  return peak

def fromPeakToThreshold(x, realPeak):
    thresh_max = 200
    X = X[realPeak:]
    valley = np.argmin(X)
    return min(thresh_max, valley)

def fromPeakToThreshold(X, realPeak):
    def findValley():
      valley = 1
      for i in range(realPeak[0], 201):
        valley = min(valley, X[i])
      
      digit = 0
      mult = 1
      temp = valley
      while temp < 1:
        temp *= 10
        mult *= 10
        digit += 1

      return valley, mult, digit
    
    i = realPeak[0]
    valley, mult, digit = findValley()

    thresh = 200 # if not found any valley, therefore always monotonic decrease, then the thresh value would be the biggest possible pixel value
    thresh_val = round(valley + (1 / mult), digit)
    for i in range(i + 1, 201):
        if X[i - 1] >= X[i] and X[i + 1] > X[i]:
            if X[i] <= thresh_val:
                thresh = i
        i += 1
      

    return thresh
     
def getPartitions(objs):
    partitions = []
    objs.sort(key = lambda x:x[0][0]) # sort based on min_i value
    upper = objs[0][1][0]
    lower = objs[0][0][0]
    start = 0
    for i in range(1, len(objs)):
        if objs[i][0][0] < upper:
            upper = objs[i][1][0]
            continue
        
        lower, upper = objs[i][0][0], objs[i][1][0]
        partitions.append(objs[start: i])
        start = i
    
    # edge cases
    partitions.append(objs[start : len(objs)])
    return partitions
    
