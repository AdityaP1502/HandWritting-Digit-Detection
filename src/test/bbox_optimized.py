import numpy as np
from os.path import abspath
import matplotlib.pyplot as plt
from time import time

DATA_PIXELS_INTENSITY = 0
BACKGOURND_PIXELS_INTENSITY = 127

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
    
    self.objects = []
    
  def __updateFunc(self, obj, new_loc : list[list[object]]):
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
      
  def __tranverseNode(self, start, frames, obj_id):
    img = self.img
    
    stack = [start]
    [start_i, start_j], [end_i, end_j] = frames
    
    objs = [[start.y, start.x], [start.y, start.x]]
    img[start.x][start.y] = obj_id
    
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
          
          if (dx == 0 and dy == 0): continue 
          if (i_new < start_i or i_new > end_i): continue
          if (j_new < start_j or j_new > end_j): continue
          if img[i_new][j_new] != DATA_PIXELS_INTENSITY: continue
          
          img[i_new][j_new] = obj_id
          stack.append(Position(i_new, j_new))
          
          objs[0][0] = min(objs[0][0], i_new)
          objs[0][1] = min(objs[0][1], j_new) 
          objs[1][0] = max(objs[1][0], i_new) 
          objs[1][1] = max(objs[1][1], j_new) 
            
    return objs
    
  def __findEntryPoint(self, pos, loc):
    img = self.img
    
    nx = self.nx
    ny = self.ny
    
    i = pos.y
    j = pos.x
    
    # Base case
    if (i > self.nx or i < 0 or j > self.ny or j < 0): return None
    if img[i][j] == DATA_PIXELS_INTENSITY: return pos
    
    if loc == 1:
      k = j
      while k < nx and img[i + 1][k] != BACKGOURND_PIXELS_INTENSITY:
        k += 1
        if (img[i][k] == DATA_PIXELS_INTENSITY): return Position(i, k)
      
      k = i
      while k > 0 and img[k][j - 1] != BACKGOURND_PIXELS_INTENSITY:
        k += -1
        if (img[k][i] == DATA_PIXELS_INTENSITY): return Position(k, j)
        
    elif loc == 2:
      k = j
      while k > 0 and img[i - 1][k] != BACKGOURND_PIXELS_INTENSITY:
        k += -1
        if (img[i][k] == DATA_PIXELS_INTENSITY): return Position(i, k)
      
      k = i
      while k > 0 and img[k][j + 1] != BACKGOURND_PIXELS_INTENSITY:
        k += -1
        if (img[k][j] == DATA_PIXELS_INTENSITY): return Position(k, j)
    
    elif loc == 3:
      k = j
      while k > 0 and img[i + 1][k] != BACKGOURND_PIXELS_INTENSITY:
        k += -1
        if (img[i][k] == DATA_PIXELS_INTENSITY): return Position(i, k)
      
      k = i
      while k < ny and img[k][j + 1] != BACKGOURND_PIXELS_INTENSITY:
        k += 1
        if (img[k][i] == DATA_PIXELS_INTENSITY): return Position(k, j)
    
    elif loc == 4:
      k = j
      while k < nx and img[i - 1][k] != BACKGOURND_PIXELS_INTENSITY:
        k += 1
        if (img[i][k] == DATA_PIXELS_INTENSITY): return Position(i, k)
      
      k = i
      while k < ny and img[k][j - 1] != BACKGOURND_PIXELS_INTENSITY:
        k += 1
        if (img[k][i] == DATA_PIXELS_INTENSITY): return Position(k, j)
  
    return None
  
  def __getShape(self, center, obj_id):
    img = self.img
    i = center.y
    j = center.x
    
    temp_y = i
    temp_x = j + 1
    ref = [[center.y, center.x], [center.y, center.x]]
    
    # while temp_x < self.nx and img[temp_y][temp_x] == DATA_PIXELS_INTENSITY:
    #   img[temp_y][temp_x] = obj_id
    #   ref[1][1] = temp_x
    #   temp_x += 1
      
    # temp_y = i
    # temp_x = j - 1
    
    # while temp_x > 0 and img[temp_y][temp_x] == DATA_PIXELS_INTENSITY:
    #   img[temp_y][temp_x] = obj_id
    #   ref[0][1] = temp_x
    #   temp_x += -1
    
    # temp_y = i + 1
    # temp_x = j
    
    # while temp_y < self.ny and img[temp_y][temp_x] == DATA_PIXELS_INTENSITY:
    #   img[temp_y][temp_x] = obj_id
    #   ref[1][0] = temp_y
    #   temp_y += 1
      
    # temp_y = i - 1
    # temp_x = j
    
    # while temp_y > 0 and img[temp_y][temp_x] == DATA_PIXELS_INTENSITY:
    #   img[temp_y][temp_x] = obj_id
    #   ref[0][0] = temp_x
    #   temp_y += -1
    
    # entry_points = [
    #     None,
    #     None,
    #     None,
    #     None,
    # ]
    
    end_points = [
      Position(0, self.nx), 
      Position(0, 0), 
      Position(0, self.ny), 
      Position(self.nx, self.ny)
    ]
    
    obj = []
    for i in range(1, 5):
      sum_y = end_points[i - 1].y + entry_points[i - 1].y
      #   sum_x = end_points[i - 1].x + entry_points[i - 1].x
        
      #   frames = [[None, None], [None, None]]
        
      #   frames[0][0] = min(end_points[i - 1].y, entry_points[i - 1].y) # min i frames
      #   frames[0][1] = min(end_points[i - 1].x, entry_points[i - 1].x) # min j frames
      #   frames[1][0] = sum_y - frames[0][0]  # max i frames
      #   frames[1][1] = sum_x - frames[0][1] # max j frames
        
      #   new_obj = self.__tranverseNode(Position(entry_points[i - 1].y, entry_points[i - 1].x), frames, obj_id)
      #   obj.append(new_obj)
    # for i in range(1, 5):
      # entry_points[i - 1] = self.__findEntryPoint(center, i)
      # if (entry_points[i - 1] != None):
      #   sum_y = end_points[i - 1].y + entry_points[i - 1].y
      #   sum_x = end_points[i - 1].x + entry_points[i - 1].x
        
      #   frames = [[None, None], [None, None]]
        
      #   frames[0][0] = min(end_points[i - 1].y, entry_points[i - 1].y) # min i frames
      #   frames[0][1] = min(end_points[i - 1].x, entry_points[i - 1].x) # min j frames
      #   frames[1][0] = sum_y - frames[0][0]  # max i frames
      #   frames[1][1] = sum_x - frames[0][1] # max j frames
        
      #   new_obj = self.__tranverseNode(Position(entry_points[i - 1].y, entry_points[i - 1].x), frames, obj_id)
      #   obj.append(new_obj)
        
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
          obj_id += 2
          
          
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
          
def createTestImg(number):
  f = open(abspath("src/test/testData/{}.txt".format(number)))
  lines = map(lambda x: x.replace("\n", ""), f.readlines())
  pixels = []
  for line in lines:
    pixels.append(list(map(lambda x: int(x), line.split(","))))
  
  # pixels = np.array(pixels, dtype=c_ubyte)
  return pixels
   
if __name__ == "__main__":
  pixels = createTestImg("4")
  ny, nx = np.shape(pixels)
  
  plt.imshow(pixels, cmap='gray', vmin=0, vmax=255)
  plt.show()
  
  start_time = time()
  bbox = BoundingBox_Optimized(pixels)
  bbox.find()
  end_time = time()
  print((end_time - start_time) * 1000, 'ms')
  
  objs = bbox.objects
  result = BoundingBox_Optimized.createBoudingBox(pixels, objs)
  plt.imshow(result, cmap='gray', vmin=0, vmax=255)
  plt.show()
  
          
          
    
      
    
      