#!/usr/bin/env python
# coding: utf-8

# # Import Library 

# In[1]:


# Run this if you start using this notebook for the first time
#import sys
from os import getcwd, mkdir
#!{sys.executable} -m pip install -r "../../requirements.txt"


# In[2]:


import cv2
import numpy as np
import matplotlib.pyplot as plt
import PIL
import scipy.ndimage as sciim
from scipy.signal import savgol_filter
from os.path import abspath
from time import time
from ctypes import *
print(abspath(""))
IMG_DIRPATH = "../../img/"
SO_DIRPATH = "../libs/"


# # Load  C Shared Library 

# In[3]:


class Image(Structure):
  _fields_ = [
    ("img", c_void_p), 
    ("nx", c_int), 
    ("ny", c_int), 
  ]
class Position(Structure):
   _fields_ = [
     ("x", c_uint32), 
     ("y", c_uint32), 
   ]
class Data(Structure):
  _fields_ = [
    ("object", POINTER(POINTER(POINTER(Position)))), 
    ("length", c_int)
  ]

SO_FILE_BBOX = abspath("../libs/libbbox.so")
bbox_c = CDLL(SO_FILE_BBOX)
bbox_c.python_bbox_find.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
bbox_c.python_bbox_find.restype = POINTER(Data)


# In[46]:


def serializeArray(pixels, nx, ny):
    total_pixels = nx * ny
    x = [0 for i in range(total_pixels)]
    for i in range(total_pixels):
        x[i] = pixels[i // nx][i % nx]
  
    return np.array(x, dtype=np.ubyte)

def bbox_pipeline(img : np.ndarray):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 2), "Image must be a grayscale image. Pixels matrix must have only two dimensions"
  
    ny, nx = shape
    pixels_serialize = serializeArray(img, nx, ny)
  
    try:
        data_ptr = bbox_c.python_bbox_find(pixels_serialize, nx, ny)
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined bbox. Make sure to load bbox library first before running this function\n")
        print("Make sure to defined the restype and argtype of bbox_python_find")
        exit(-1)
  
    
    data : Data = data_ptr.contents
    arr_of_arr_of_pos_ptr = data.object
    arr_length = data.length
    objs = []
  
    for i in range(arr_length):
        arr_of_pos_ptr = arr_of_arr_of_pos_ptr[i]
        pos_min = arr_of_pos_ptr[0].contents
        pos_max = arr_of_pos_ptr[1].contents
    
        objs.append([[pos_min.y, pos_min.x], [pos_max.y, pos_max.x]])
        
    return objs
    #print(objs)
    #result = BoundingBox.createBoudingBox(img, objs)
    #showPicture(result, False)
    ##plt.show()


# # Plotting Utility Function

# In[5]:


def showPicture(pixels, isRGB, caption=""):
    if isRGB:
        fig = plt.figure()
        plt.axis("off")
        img_RGB = cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB)
        plt.title(caption)
        plt.imshow(img_RGB)
        #plt.show()
    else:
        fig = plt.figure()
        plt.axis("off")
        plt.title(caption)
        plt.imshow(pixels, cmap='gray', vmin=0, vmax=255)
        #plt.show()
        
    


# # Shadow Removal Class

# In[6]:


class ShadowRemoval():
  def __init__(self, img):
    self.img = img
    self.kernel = np.ones((7, 7), np.uint8)
    self.output = None

  def backgroudRemoval(self):
    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG() 
    self.output = fgbg.apply(self.img.pixels)

  def remove(self, iterations=1):
    rgb_planes = cv2.split(self.img.pixels)
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((11,11), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        result_norm_planes.append(norm_img)
    shadowremov = cv2.merge(result_norm_planes)
    self.output = shadowremov
    
    

  def update(self):
    self.img.pixels = self.output


# # Image Class

# In[7]:


class Image():
    def __init__(self, filename) -> None:
        self.pixels = cv2.imread(filename)
        self.backup = None

    def toGrayscale(self):
      self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
      
    def invertColor(self, thresh):
      min = 0
      max = thresh
      ny, nx = np.shape(self.pixels)
      for i in range(ny):
        for j in range(nx):
          if min <= self.pixels[i][j] <= max:
            self.pixels[i][j] = 255
          else:
            self.pixels[i][j] = 0

    def accentPicture(self, iterations=1):
      self.pixels = cv2.erode(self.pixels, np.ones((7,7), np.uint8), iterations=iterations)

    def doBackup(self):
      self.backup = np.copy(self.pixels)

    def restart(self):
      self.pixels = np.copy(self.backup)

    def show(self, txt):
        fig = plt.figure()
        plt.axis("off")
        fig.text(.5, 0.12, txt, ha = 'center')
        plt.imshow(self.pixels, cmap = 'gray')
        #plt.show()


# # Bounding Box Class
# Bounding box to detect shape in images

# In[8]:


class Node():
    def __init__(self, id : int, pos):
        self.root = None
        self.id   = id
        self.pos  = pos
  
    def getRoot(self) -> "Node":
        node = self
        while (node.root != None):
            node = node.root
      
        return node
  
    def getID(self) -> int:
        return self.getRoot().id
      
    def __eq__(self, __o: object) -> bool:
        # would run in O(N_OBJ) time
        if type(self) == type(__o):
            return self.getID() == __o.getID()
    
        else:
            return False
  
    def updateValue(self, new_value, fnc) -> None:
        root = self.getRoot()
        fnc(root.pos, new_value)
    
    @classmethod
    def resolvedNodeConflict(cls, roots, resolve_fnc) -> None:
        # nodes will have max length of 4, and getRoot would need log(N_OBJ)
        # therefore will run in log(N_OBJ) time
        newRootVal = resolve_fnc(roots)
        newID = roots[0].id
        newRoot = cls(newID, newRootVal)
    
        for root in roots:
            root.root = newRoot
            root.pos = None
    
        return newID


# In[63]:


class BoundingBox():
    def __init__(self, pixels):
        self.img = pixels
        self.objects = [] # list of shape
        self.result = np.copy(pixels)
        
    def find(self):
        # search object
        self.__searchObjects()
    
    def resolveFunc(self, roots):
      ref = roots[0].pos
      for i in range(1, len(roots)):
        self.updateFunc(ref, roots[i].pos)
      
      return ref
  
    def updateFunc(self, obj, new_loc):
      # In place change the object data
      if len(new_loc) == 1:
          new_loc_i1, new_loc_j1 = new_loc[0]
          new_loc_i2 = new_loc_i1
          new_loc_j2 = new_loc_j1
      else:
          [new_loc_i1, new_loc_j1], [new_loc_i2, new_loc_j2] = new_loc
          
      [min_i, min_j], [max_i, max_j] = obj
      
      obj[0][0] = min(new_loc_i1, min_i)
      obj[0][1] = min(new_loc_j1, min_j)
      obj[1][0] = max(new_loc_i2, max_i)
      obj[1][1] = max(new_loc_j2, max_j)
                
    def __updateObject(self, member_id, *new_loc):
        obj_node : Node = self.objects[member_id - 1]
        obj_node.updateValue([new_loc], self.updateFunc)
                   
    def __resolvedConflict(self, roots):
      return Node.resolvedNodeConflict(roots, self.resolveFunc)
        
    def __createObject(self, *location):
        location = list(location)
        new_node = Node(len(self.objects) + 1, [location, location[:]])
        self.objects.append(new_node)
        return new_node.id
    
    def __searchObjects(self):
        n_i, n_j = np.shape(self.img)
        # upper stram and box consist of member_id of each pixels. Member_id indicate which object this pixels belong to
        # upper_stream holds data for all pixels on the upper side of current pixel
        # box holds data for pixel on the left of current pixel
        # the smallest id is 1, 0 -> no member
        upper_stream = [0 for i in range(n_j)]
        box = 0
        # scan each pixels, going from upper left to lower right
        for i in range(n_i):
          for j in range(n_j):  
            if self.img[i][j] == 0: 
              if box != 0:
                upper_stream[j - 1] = box
                box = 0
              continue
            # because going from upper left to lower right, only need to check pixel from upper and left
            conflict = False
            dict = {box : True} if box != 0 else {}
 
            # check upper if exist
            if i - 1 >= 0:
              for k in range(j - 1, j + 2):
                if k < n_j and self.img[i - 1][k] != 0:
                    if dict.get(upper_stream[k], False) == True:
                      continue
                    if len(dict) == 0:
                      dict[upper_stream[k]] = True
                    
                    # Check for conflict
                    elif len(dict) == 1:
                      roots = []
                      id1 = list(dict.keys())[0]
                      id2 = upper_stream[k]
                      
                      root1 = self.objects[id1 - 1].getRoot()
                      root2 = self.objects[id2 - 1].getRoot()
                      if (root1 != root2):
                        conflict = True
                        roots.append(root1)
                        roots.append(root2)
                        dict[upper_stream[k]] = True
                    
                    elif len(dict) > 1:
                      id3 = upper_stream[k]
                      root3 = self.objects[id3 - 1].getRoot()
                      for root in roots:
                        if (root != root3):
                          roots.append(root3)
                          dict[upper_stream[k]] = True

            if len(dict) == 0:
                # create new object
                member_id = self.__createObject(i, j)
            else:  
              if not conflict:
                  # determine member id
                  member_id = list(dict.keys())[0]
                  # update object
                  self.__updateObject(member_id, i, j)
              else:
                  # resolved conflict, connected object can't have more than one member_id
                  member_id = self.__resolvedConflict(roots)

            # update upper stream value and box
            if box == 0:
                box = member_id

            elif box != 0:
                upper_stream[j - 1] = box
                box = member_id
    
    def getObjects(self):
        dict = {}
        for i in range(len(self.objects)):
            root = self.objects[i].getRoot()
            if dict.get(root.id, None) != None:
                continue
            dict[root.id] = root.pos
        objs = list(dict.values())
        return objs
    
    @staticmethod
    def createBoundingBox(img, shapes):
        result = np.copy(img)
        
        for shape in shapes:
            [min_i, min_j], [max_i, max_j] = shape
          
            for i in range(min_i, max_i + 1):
                result[i][min_j] = 255
                result[i][max_j] = 255
          
            for j in range(min_j, max_j + 1):
                result[min_i][j] = 255
                result[max_i][j] = 255
          
        return result


# In[10]:


# BoundingBox Optimized Version
DATA_PIXELS_INTENSITY = 255
BACKGOURND_PIXELS_INTENSITY = 0

class Position:
  def __init__(self, y, x) -> None:
    self.x = x
    self.y = y

class BoundingBox_Optimized():
  def __init__(self, img) -> None:
    self.img = img
    
    ny, nx = np.shape(img)
    self.ny = ny
    self.nx = nx
    self.f = open('out.txt', 'r+')
    
    self.objects = []
    
  def __updateFunc(self, obj, new_loc):
      # In place change the object data
      if len(new_loc) == 1:
          new_loc_i1, new_loc_j1 = new_loc[0]
          new_loc_i2 = new_loc_i1
          new_loc_j2 = new_loc_j1
      else:
          [new_loc_i1, new_loc_j1], [new_loc_i2, new_loc_j2] = new_loc
          
      [min_i, min_j], [max_i, max_j] = obj
      
      obj[0][0] = min(new_loc_i1, min_i)
      obj[0][1] = min(new_loc_j1, min_j)
      obj[1][0] = max(new_loc_i2, max_i)
      obj[1][1] = max(new_loc_j2, max_j)
      
  def __tranverseNode(self, start, frames, obj_id, min_id, max_id):
    img = self.img
    
    stack = [start]
    [start_i, start_j], [end_i, end_j] = frames
    
    objs = [[start.y, start.x], [start.y, start.x]]
    img[start.y][start.x] = obj_id
    
    dx_s = [-1, 0, 1]
    dy_s = [-1, 0, 1]
    
    while len(stack) > 0:
      curr_pos = stack.pop()
      i = curr_pos.y
      j = curr_pos.x
      
      for dx in dx_s:
        for dy in dy_s:
          i_new = i + dx
          j_new = j + dy
          
          if (i_new < start_i or i_new > end_i): continue
          if (j_new < start_j or j_new > end_j): continue

          if (img[i_new][j_new] != DATA_PIXELS_INTENSITY): 
            # ignore any pixels that has id value outside range
            if img[i_new][j_new] > max_id or img[i_new][j_new] < min_id: continue
            # if process by current block, don't re process
            if img[i_new][j_new] == obj_id: continue

          img[i_new][j_new] = obj_id
          stack.append(Position(i_new, j_new))
          objs[0][0] = min(objs[0][0], i_new)
          objs[0][1] = min(objs[0][1], j_new) 
          objs[1][0] = max(objs[1][0], i_new) 
          objs[1][1] = max(objs[1][1], j_new) 
            
    return objs
    
  def __getShape(self, center, obj_id):
    i = center.y
    j = center.x
    
    ref = [[center.y, center.x], [center.y, center.x]]
    
    end_points = [
      Position(0, self.nx - 1), 
      Position(0, 0), 
      Position(self.ny - 1, 0), 
      Position(self.ny - 1, self.nx - 1)
    ]
    
    obj = []
    frames = [[None, None], [None, None]]

    min_obj_id = obj_id
    max_obj_id = min_obj_id + 6

    obj_id = min_obj_id
    for i in range(1, 5):
      sum_x = end_points[i - 1].x + center.x
      sum_y = end_points[i - 1].y + center.y
    
      frames[0][0] = min(end_points[i - 1].y, center.y)
      frames[0][1] = min(end_points[i - 1].x, center.x)
      frames[1][0] = sum_y - frames[0][0]
      frames[1][1] = sum_x - frames[0][1]
      
      new_obj = self.__tranverseNode(center, frames, obj_id, min_obj_id, max_obj_id)
      obj.append(new_obj)
      obj_id += 2
    
    # Update min max value
    for i in range(len(obj)):
      self.__updateFunc(ref, obj[i])
      
    return ref
  
  def find(self):
    obj_id = 2
    for i in range(self.ny):
      for j in range(self.nx):
        if (self.img[i][j] == BACKGOURND_PIXELS_INTENSITY): continue 
        if (self.img[i][j] == DATA_PIXELS_INTENSITY):
          shape = self.__getShape(Position(i, j), obj_id)
          self.objects.append(shape)
          obj_id += 8

    self.f.close()
          
          
  @staticmethod
  def createBoudingBox(img, shapes):
    result = np.copy(img)

    for shape in shapes:
      [min_i, min_j], [max_i, max_j] = shape

    for i in range(min_i, max_i + 1):
      result[i][min_j] = 255
      result[i][max_j] = 255

    for j in range(min_j, max_j + 1):
      result[min_i][j] = 255
      result[max_i][j] = 255

    return result


# # Helper Function

# In[11]:


def shiftImage(img, shift):
    return sciim.shift(img, shift)

def scaleImage(img, show):
    dim = (28, 28)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    if show:
        showPicture(resized, False, "After Scaling")
    return resized

def centerImage(img):
    # create an image with 1 : 1 aspect ratio
    ny, nx = np.shape(img)
    dim = max(nx, ny)
    a = np.zeros((dim, dim))
    for i in range(ny):
        for j in range(nx):
            a[i][j] = img[i][j]
    
    # shift image so the shape in the center
    dx = (dim - nx) / 2
    dy = (dim - ny) / 2
    return shiftImage(a, (dy, dx))

def getShape(x, obj, show=False):
    [min_i, min_j], [max_i, max_j] = obj
    py = (max_i - min_i) + 1
    px = (max_j - min_j) + 1
    
    shape = np.zeros((py, px))
    
    start_i = min_i
    start_j = min_j
    
    for i in range(py):
        for j in range(px):
            shape[i][j] = x[start_i + i][start_j + j]
    if show:
        showPicture(shape, False, "Before Scaling")
    return scaleImage(centerImage(shape), show)

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
        
    return partitions
    
def sortObjs(objs):
    partitions = getPartitions(objs)
    sortedObjs = []
    for partition in partitions:
        partition.sort(key = lambda x: x[0][1]) # sort based on min j
        for obj in partition:
            sortedObjs.append(obj)
            
    return sortedObjs


# # Image preprocess
# 1. Remove Shadow
# 
# ---
# 
# 
# 2. Convert to grayscale
# 
# ---
# 
# 
# 3. Invert color (background will be black __(0)__ text will be white __(255)__)

# In[12]:


FILENAME = "301914.jpg"
try:
    mkdir(abspath("../../out/{}".format(FILENAME)))
except:
    pass


# In[13]:


try:
     mkdir(abspath("../../out/{}/detected_shapes".format(FILENAME)))
except:
    pass


# In[14]:


IMG_FILEPATH = IMG_DIRPATH + FILENAME


# In[ ]:





# In[15]:


# load image
img2 = Image(IMG_FILEPATH)
img2.toGrayscale()


# In[16]:


showPicture(img2.pixels, True)


# In[17]:


shr2 = ShadowRemoval(img2)
shr2.remove()


# In[18]:


showPicture(shr2.output, True)


# Hasil shadow removal

# In[19]:


shr2.update()
#img2.accentPicture()


# In[20]:


showPicture(img2.pixels, True)


# # Image pixels density graph

# In[21]:


# import seaborn as sns
# def plotDensity(img):
#   x = img2.pixels.reshape(1, -1)[0]
#   sns.set_style('whitegrid')
#   plt.xlim(0, 255)
#   X, Y = sns.kdeplot(x, bw=0.5, gridsize=500).get_lines()[0].get_data()
#   return X, Y


# In[22]:


# plotDensity(img2.pixels)


# # Image Thresholding

# In[23]:


def fromPixelsToHistogram(img):
    id = np.array([i for i in range(0, 256)])
    x = np.array([0 for i in range(0, 256)])
    Y = img.pixels.reshape(1, -1)[0] # change matrix into an array

    for pix_val in Y:
      x[pix_val] += 1     
    window = 21
    order = 2

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

def fromPeakToThreshold(X, realPeak, max_dist_percentage=0.1):
    def findValley():
      valley = 1
      for i in range(realPeak[0], 201):
        valley = min(valley, X[i])
      
      digit = 0
      mult = 1
      temp = valley * 1
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
      print(i, X[i])
      if X[i - 1] > X[i] and X[i + 1] > X[i]:

        if X[i] <= thresh_val:
          thresh = i

      last_value = X[i]
      i += 1
      

    return thresh


# 

# In[24]:


X = fromPixelsToHistogram(img2)


# In[25]:


peak = findPeak(X)


# In[26]:


peak


# In[27]:


thresh = fromPeakToThreshold(X, peak)


# In[28]:


thresh


# In[29]:


thresh


# In[30]:


# run this to backup image
img2.doBackup()


# In[31]:


showPicture(img2.backup, True)


# # Invert Image and Save Result

# In[32]:


start_time = time()
img2.invertColor(thresh)
end_time = time()
print((end_time - start_time) * 1000, "ms")


# In[33]:


showPicture(img2.pixels, True)


# In[34]:


# save result in root/out
path = abspath("../../out/{}/frame_out.png").format(FILENAME)
img_new = PIL.Image.fromarray(img2.pixels, mode="L")
img_new.save(path, mode="L")


# In[35]:


# run this to restart images to last state
# img2.restart()


# In[36]:


showPicture(img2.pixels, True)


# # Bounding Box
# Bounding box is the the smallest rectangles that encapsulate an object (for our case is a number)
# To find bounding box, first find all connected pixels, then from connected pixels store the minP and maxP. Then from there, we can construct the bounding box
# 
# Algorithm Complexity is:
# Time : $O(NM * log(N_{object}))$
# Space : $O(min(N, M) + N_{object})$

# In[51]:


start_time = time()
objs = bbox_pipeline(img2.pixels)
end_time = time()
print((end_time - start_time) * 1000, "ms")


# In[53]:


res = BoundingBox.createBoundingBox(img2.pixels, objs)
showPicture(res, False)


# In[60]:


bbox = BoundingBox(img2.pixels)


# In[64]:


start_time = time()
bbox.find()
objs = bbox.getObjects()
end_time = time()
print((end_time - start_time) * 1000, "ms")


# In[65]:


res = BoundingBox.createBoundingBox(img2.pixels, objs)
showPicture(res, False)


# In[ ]:


# save result in root/out
path = abspath("../../out/{}/frame_out_bbox.png").format(FILENAME)
img_new = PIL.Image.fromarray(bbox.result, mode="L")
img_new.save(path, mode="L")


# In[66]:


bbox_opt = BoundingBox_Optimized(img2.pixels)


# In[73]:


start_time = time()
bbox_opt.find()
objs = bbox_opt.objects
end_time = time()
print((end_time - start_time) * 1000, "ms")


# In[74]:


res = BoundingBox.createBoundingBox(img2.pixels, objs)
showPicture(res, False)


# In[80]:


# save result in root/out
path = abspath("../../out/{}/frame_out_bbox.png").format(FILENAME)
img_new = PIL.Image.fromarray(res, mode="L")
img_new.save(path, mode="L")


# # Get Detected Shape
# Get detected shape from bbox then scale the the image
# resolution of the image must be 28 x 28 pixels

# In[ ]:





# In[ ]:


showPicture(img2.pixels, False)


# In[76]:


s = bbox_opt.objects


# In[77]:


s = sortObjs(s)


# In[78]:


for obj in s:
    shape = getShape(img2.pixels, obj, show=True)


# # Output

# In[ ]:


numbers = []
for obj in s:
    shape = getShape(img2.pixels, obj)
    numbers.append(shape)


# Numbers adalah list dari gambar objek(Angka) yang dideteksi oleh sistem. Gambar direpresentasikan dengan array of pixels. 

# # References
# [1]. https://stackoverflow.com/questions/4150171/how-to-create-a-density-plot-in-matplotlib </br>
# [2]. https://www.geeksforgeeks.org/erosion-dilation-images-using-opencv-python/ </br>
# [3]. https://medium.com/arnekt-ai/shadow-removal-with-open-cv-71e030eadaf5
