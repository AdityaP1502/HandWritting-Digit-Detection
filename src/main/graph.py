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
  
      
  
  
  