import numpy as np
import matplotlib.pylab as plt
from shape import Node
from time import time
from os.path import abspath
from ctypes import *
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
class BoundingBox():
    def __init__(self, pixels):
        self.img = pixels
        self.objects = [] # list of shape
        self.result = np.copy(pixels)
        
    def find(self):
        # search object
        self.__searchObjects()
        # then create bounding box using data from self.objects
        self.__createBoudingBox()
    
    def resolveFunc(self, roots):
      ref = roots[0].pos
      for i in range(1, len(roots)):
        self.updateFunc(ref, roots[i].pos)
      
      return ref
  
    def updateFunc(self, obj, new_loc : list[list[object]]):
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
                
    def __updateObject(self, member_id : int, *new_loc : tuple[int]):
        obj_node : Node = self.objects[member_id - 1]
        obj_node.updateValue([new_loc], self.updateFunc)
                   
    def __resolvedConflict(self, roots : list[Node]):
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
                    
    def getObject(self):
      dict = {}
      for i in range(len(self.objects)):
        root = self.objects[i].getRoot()
        if dict.get(root.id, None) != None:
          continue
        dict[root.id] = root.pos
      return list(dict.values())
        
    @staticmethod
    def createBoudingBox(img, shapes):
        result = np.copy(img)
        
        for shape in shapes:
          [min_i, min_j], [max_i, max_j] = shape
          
        for i in range(min_i, max_i + 1):
          result[i][min_j] = 127
          result[i][max_j] = 127
          
        for j in range(min_j, max_j + 1):
          result[min_i][j] = 127
          result[max_i][j] = 127
          
        return result
          
    
def createTestImg(number):
  f = open(abspath("src/test/testData/{}.txt".format(number)))
  lines = map(lambda x: x.replace("\n", ""), f.readlines())
  pixels = []
  for line in lines:
    pixels.append(list(map(lambda x: int(x), line.split(","))))
  
  # pixels = np.array(pixels, dtype=c_ubyte)
  return pixels

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
    data_ptr = bbox.python_bbox_find(pixels_serialize, nx, ny)
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
    
  result = BoundingBox.createBoudingBox(pixels, objs)
  plt.imshow(result, cmap='gray', vmin=0, vmax=255)
  plt.show()
  
if __name__ == "__main__":
  SO_FILE_BBOX = abspath("src/libs/libbbox.so")
  bbox = CDLL(SO_FILE_BBOX)
  bbox.python_bbox_find.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
  bbox.python_bbox_find.restype = POINTER(Data)
  
  pixels = createTestImg("4")
  ny, nx = np.shape(pixels)
  bbox_pipeline(pixels)
  
  # pixels_serialize = serializeArray(pixels, nx, ny)
  # # print(pixels)
    
  # # start_time = time()
  # # bbox = BoundingBox(pixels=pixels)
  # # bbox.find()
  # # print(bbox.getObject())
  # # end_time = time()
  
  # # print((end_time - start_time) * 1000, "ms")
  # # plt.imshow(bbox.result, cmap="gray")
  # # plt.show()
  
  # # pixels = np.ascontiguousarray(pixels)
  
  
  
  