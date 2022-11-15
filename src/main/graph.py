# class Vertex():
#   def __init__(self, key) -> None:
#     self.key = key
#     # 0 : left, 1 : down, 2 : right, 3 : up
#     self.conn = [None for i in range(4)]
    
#   def add_connection(self, vertex, direction):
#     self.conn[direction] = vertex
    
#   def findLoop():
#     pass
  
#   @staticmethod
#   def connectionDirection(a, b):
#     # direction from a to b
#     direction = [0, 0, 0, 0] # left, down, right, up
#     if a.i < b.i:
#       # up
#       direction[3] = 1
    
#     elif a.i > b.i:
#       # down
#       direction[1] = 1
      
#     if a.j < b.j:
#       # right
#       direction[2] = 1
      
#     elif a.j > b.j:
#       # left
#       direction[0] = 1
    
#     return direction
  
#   def tranverseNode(self, dict = {}):
#     dir_type = ["left", "down", "right", "up"]
    
#     dict[self.key.i, self.key.j] = True
#     for conn in self.conn:
#       if conn == None: continue
#       dirs = ""
#       dir_vector = self.connectionDirection(self.key, conn.key)
      
#       for i, vector in enumerate(dir_vector):
#         if vector == 1:
#           dirs += dir_type[i]
          
#       print("{} connected to {} by going {}".format(self.key, conn.key, dirs))
    
#     for conn in self.conn:
#       if conn == None: continue
#       if dict.get((conn.key.i, conn.key.j), False) == True:
#         continue
#       conn.tranverseNode(dict)

#   def n_loop(self, in_vertex):
#     total = 0
#     dict[self.key.i, self.key.j] = True
    
#     return total
      
  
class Vertex():
  def __init__(self, key) -> None:
    self.key = key
    self.conn = []
    
  def add_connection(self, vertex):
    self.conn.append(vertex)
    
  def findLoop():
    pass
  
  @staticmethod
  def connectionDirection(a, b):
    # direction from a to b
    direction = [0, 0, 0, 0] # left, down, right, up
    if a.i < b.i:
      # up
      direction[3] = 1
    
    elif a.i > b.i:
      # down
      direction[1] = 1
      
    if a.j < b.j:
      # right
      direction[2] = 1
      
    elif a.j > b.j:
      # left
      direction[0] = 1
    
    return direction
  
  def tranverseNode(self):
    dir_type = ["left", "down", "right", "up"]
    for conn in self.conn:
      dirs = ""
      dir_vector = self.connectionDirection(self.key, conn.key)
      
      for i, vector in enumerate(dir_vector):
        if vector == 1:
          dirs += dir_type[i]
          
      print("{} connected to {} by going {}".format(self.key, conn.key, dirs))
    
    for conn in self.conn:
      conn.tranverseNode()
  