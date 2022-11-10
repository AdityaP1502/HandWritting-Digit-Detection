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
    newID = roots[-1].id # random new ID
    
    newRoot = cls(newID, newRootVal)
    
    for root in roots:
      root.root = newRoot
      root.pos = None
    
    return newID
    
    
  