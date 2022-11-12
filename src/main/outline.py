import numpy as np
from src.main.graph import Vertex
from os.path import abspath
from ctypes import *
# class Position():
#   def __init__(self, i, j) -> None:
#     self.i = i
#     self.j = j
  
#   def __eq__(self, __o: object) -> bool:
#     if __o.i == None:
#       return __o.j == self.j
    
#     if __o.j == None:
#       return __o.i == self.i
    
#     return (self.i == __o.i and self.j == __o.j)
  
#   def __repr__(self) -> str:
#     return '({}, {})'.format(self.i, self.j)

# class Outline():
#   def __init__(self, img) -> None:
#     ny, nx = np.shape(img)
#     # self.img = np.full((ny+1, nx + 1), 255)

#     # for i in range(1, ny + 1):
#     #   for j in range(1, nx + 1):
#     #     self.img[i][j] = img[i - 1][j - 1]
#     # print(self.img)
#     self.img = img
#     self.ny = ny
#     self.nx = nx
    
#     self.update_pos = [
#       self.__updateFnc_1, 
#       self.__updateFnc_2, 
#       self.__updateFnc_3, 
#       self.__updateFnc_4, 
#     ]

#     self.end_pos = [
#       Position(None, -1), 
#       Position(-1, None), 
#       Position(None, nx),
#       Position(ny, None), 
#     ]
    
#     self.dp = [[None for i in range(self.nx)] for j in range(self.ny)]
  
#   @staticmethod
#   def __updateFnc_1(pos):
#     pos.j -= 1
  
#   @staticmethod
#   def __updateFnc_2(pos):
#     pos.i -= 1

#   @staticmethod
#   def __updateFnc_3(pos):
#     pos.j += 1

#   @staticmethod
#   def __updateFnc_4(pos):
#     pos.i += 1
    
#   def isBoundary(self, pos):
#     ds = [-1, 0, 1]
#     if pos.i < 0 or pos.i >= self.ny: return False
#     if pos.j < 0 or pos.j >= self.nx: return False
#     if self.img[pos.i][pos.j] == 255: return False
    
#     for dy_ in ds:
#       for dx_ in ds:
#         i = pos.i + dy_
#         j = pos.j + dx_

#         if i < 0 or i >= self.ny: return True
#         if j < 0 or j >= self.nx: return True

#         if self.img[i][j] == 255:
#           return True
      
#     return False

#   def getNeighborBoundary(self, pos):
#     ds = [-1, 0, 1, 0]
#     loc = []
#     curr_loc = Position(None, None)
#     for k in range(4):
#       dy = ds[(k + 3) % 4]
#       dx = ds[k]
      
#       curr_loc.i = pos.i + dy
#       curr_loc.j = pos.j + dx
      
#       if curr_loc.i < 0 or curr_loc.i >= self.ny: continue
#       if curr_loc.j < 0 or curr_loc.j >= self.nx: continue
      
#       if self.isBoundary(curr_loc):
#         if self.dp[curr_loc.i][curr_loc.j] != None: continue
#         loc.append(k)
        
#     return loc
  
#   def tranverse(self, stack):
#     while len(stack) > 0:
#       root_pos, root_vertex, direction = stack.pop()
#       curr_loc = Position(root_pos.i, root_pos.j)
#       self.update_pos[direction](curr_loc)
#       exist = False

#       while (curr_loc != self.end_pos[direction] and self.isBoundary(curr_loc)):
#         dirs = self.getNeighborBoundary(curr_loc)

#         if self.dp[curr_loc.i][curr_loc.j] != None:
#           root_vertex.add_connection(self.dp[curr_loc.i][curr_loc.j], direction)
#           self.update_pos[direction](curr_loc)
#           continue

#         for direction_ in dirs:
#           if direction_ != direction:
#             exist = True
#             break
        
#         if exist:
#           new_loc = Position(curr_loc.i, curr_loc.j)

#           new_vertex = Vertex(new_loc)
#           root_vertex.add_connection(new_vertex, direction)
#           root_vertex = new_vertex

#           for direction_ in dirs:
#             if direction_ != direction:
#               stack.append([new_loc, new_vertex, direction_])

#           exist = False

#         self.dp[curr_loc.i][curr_loc.j] = root_vertex
#         self.update_pos[direction](curr_loc)
    
#   def __fill(self, img, loc, end_loc, direction):
#     ds = [-1, 0, 1, 0]
#     curr_loc = Position(loc.i, loc.j)
#     while curr_loc != end_loc:
#       for k in range(4):
#         i = curr_loc.i + ds[(3 + k) % 4]
#         j = curr_loc.j + ds[k]

#         if i < 0 or i >= self.ny: continue
#         if j < 0 or j >= self.nx: continue

#         if img[i][j] == 255:
#           img[i][j] = 127 
          
#       self.update_pos[direction](curr_loc)
        
#   def findOutline(self):
#     outlines = []
#     stack = []
#     for i in range(self.ny):
#       for j in range(self.nx):
#         if self.dp[i][j] == None:
#           start_pos = Position(i, j)
#           if not self.isBoundary(start_pos): continue
#           start_vertex = Vertex(start_pos)
#           self.dp[start_pos.i][start_pos.j] = start_vertex
#           dirs = self.getNeighborBoundary(start_pos)

#           # tranvrse new node
#           for direction in dirs:
#             stack.append([start_pos, start_vertex, direction])

#           self.tranverse(stack)
            
#           outlines.append(start_vertex)
          
#     return outlines
  
  
#   def makeOutline(self, outlines, result = [], dict = None):
#     if len(result) == 0:
#       result = np.copy(self.img)
      
#     if dict == None:
#       dict = {}

#     for outline in outlines:
#       if dict.get((outline.key.i, outline.key.j), False) == True: continue
#       dict[(outline.key.i, outline.key.j)] = True
      
#       for conn in outline.conn:
#         direction = Vertex.connectionDirection(outline.key, conn.key)
#         for k in range(4):
#           if direction[k] == 1:
#             self.__fill(result, outline.key, conn.key, k)
            
#       result = self.makeOutline(outline.conn, result)
    
#     return result
class Position():
  def __init__(self, i, j) -> None:
    self.i = i
    self.j = j
  
  def __eq__(self, __o: object) -> bool:
    if __o.i == None:
      return __o.j == self.j
    
    if __o.j == None:
      return __o.i == self.i
    
    return (self.i == __o.i and self.j == __o.j)
  
  def __repr__(self) -> str:
    return '({}, {})'.format(self.i, self.j)

class Outline():
  def __init__(self, img) -> None:
    ny, nx = np.shape(img)
    # self.img = np.full((ny+1, nx + 1), 255)

    # for i in range(1, ny + 1):
    #   for j in range(1, nx + 1):
    #     self.img[i][j] = img[i - 1][j - 1]
    # print(self.img)
    self.img = img
    self.ny = ny
    self.nx = nx
    self.isUnique = True
    self.uniqueVertexCount = 0
    
    self.update_pos = [
      self.__updateFnc_1, 
      self.__updateFnc_2, 
      self.__updateFnc_3, 
      self.__updateFnc_4, 
    ]

    self.end_pos = [
      Position(None, -1), 
      Position(-1, None), 
      Position(None, nx),
      Position(ny, None), 
    ]
    
    self.dp = [[0 for i in range(self.nx)] for j in range(self.ny)]
  
  @staticmethod
  def __updateFnc_1(pos):
    pos.j -= 1
  
  @staticmethod
  def __updateFnc_2(pos):
    pos.i -= 1

  @staticmethod
  def __updateFnc_3(pos):
    pos.j += 1

  @staticmethod
  def __updateFnc_4(pos):
    pos.i += 1
    
  def isBoundary(self, pos):
    ds = [-1, 0, 1]
    if pos.i < 0 or pos.i >= self.ny: return False
    if pos.j < 0 or pos.j >= self.nx: return False
    if self.img[pos.i][pos.j] == 255: return False
    
    for dy_ in ds:
      for dx_ in ds:
        i = pos.i + dy_
        j = pos.j + dx_

        if i < 0 or i >= self.ny: return True
        if j < 0 or j >= self.nx: return True

        if 250 <= self.img[i][j] <= 255:
          return True
      
    return False

  def getNeighborBoundary(self, pos):
    ds = [-1, 0, 1, 0]
    loc = []
    curr_loc = Position(None, None)
    for k in range(4):
      dy = ds[(k + 3) % 4]
      dx = ds[k]
      
      curr_loc.i = pos.i + dy
      curr_loc.j = pos.j + dx
      
      if curr_loc.i < 0 or curr_loc.i >= self.ny: continue
      if curr_loc.j < 0 or curr_loc.j >= self.nx: continue
      
      if self.isBoundary(curr_loc):
        if self.dp[curr_loc.i][curr_loc.j] != 0: continue
        loc.append(k)
        
    return loc

  def tranverse(self, stack):
    while len(stack) > 0:
      root_pos, root_vertex, direction = stack.pop()
      curr_loc = Position(root_pos.i, root_pos.j)
      self.update_pos[direction](curr_loc)
      exist = False

      while (curr_loc != self.end_pos[direction] and self.isBoundary(curr_loc)):
        self.dp[curr_loc.i][curr_loc.j] = 1
        dirs = self.getNeighborBoundary(curr_loc)

        for direction_ in dirs:
          if direction_ != direction:
            exist = True
            break
        
        if exist:
          # will be run atleast once
          new_loc = Position(curr_loc.i, curr_loc.j)
          new_vertex = Vertex(new_loc)
          root_vertex.add_connection(new_vertex)
          root_vertex = new_vertex

          for direction_ in dirs:
            if direction_ != direction:
              stack.append([new_loc, new_vertex, direction_])

          exist = False

        self.update_pos[direction](curr_loc)

    
  def __fill(self, img, loc, end_loc, direction):
    ds = [-1, 0, 1, 0]
    curr_loc = Position(loc.i, loc.j)
    while curr_loc != end_loc:
      for k in range(4):
        i = curr_loc.i + ds[(3 + k) % 4]
        j = curr_loc.j + ds[k]

        if i < 0 or i >= self.ny: continue
        if j < 0 or j >= self.nx: continue

        if img[i][j] == 255:
          img[i][j] = 127 
          
      self.update_pos[direction](curr_loc)
        
  def findOutline(self):
    count = 0
    outlines = []
    stack = []
    for i in range(self.ny):
      for j in range(self.nx):
        if self.dp[i][j] == 0:
          start_pos = Position(i, j)
          if not self.isBoundary(start_pos): continue
          start_vertex = Vertex(start_pos)
          dirs = self.getNeighborBoundary(start_pos)

          # tranvrse new node
          for direction in dirs:
            stack.append([start_pos, start_vertex, direction])

          self.tranverse(stack)
          
          outlines.append(start_vertex)

          if self.isUnique:
            self.uniqueVertexCount += 1

          self.isUnique = True
          
    return outlines
  
  
  def makeOutline(self, outlines, result = [], dict = None):
    if len(result) == 0:
      result = np.copy(self.img)
      
    if dict == None:
      dict = {}

    for outline in outlines:
      if dict.get((outline.key.i, outline.key.j), False) == True: continue
      dict[(outline.key.i, outline.key.j)] = True
      
      for conn in outline.conn:
        direction = Vertex.connectionDirection(outline.key, conn.key)
        for k in range(4):
          if direction[k] == 1:
            self.__fill(result, outline.key, conn.key, k)
            
      result = self.makeOutline(outline.conn, result)
    
    return result

def createTestImg(number):
  f = open(abspath("src/test/testData/{}.txt".format(number)))
  lines = map(lambda x: x.replace("\n", ""), f.readlines())
  pixels = []
  for line in lines:
    pixels.append(list(map(lambda x: int(x), line.split(","))))
  
  pixels = np.array(pixels, dtype=c_ubyte)
  return pixels


      

    
    