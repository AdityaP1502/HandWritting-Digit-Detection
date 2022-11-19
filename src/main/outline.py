import numpy as np
from src.main.graph import Vertex
from os.path import abspath
from ctypes import *

class Outline():
    __BG_PIXELS_INTENSITY = 0

    def __init__(self, img) -> None:
        ny, nx = np.shape(img)
        self.img = img
        self.ny = ny
        self.nx = nx
        self.__dp = [[0 for j in range(nx)] for i in range(ny)]

    def __checkOtherRegion(self, i, j):
        return (self.__dp[i][j] != 0)

    def __sweep(self, i, j, update_fnc, condition_fnc, end_pos):
        while j != end_pos and condition_fnc(self.img[i][j]):
            if self.__checkOtherRegion(i, j):
                break
              
            # if self.dp[i][j] != 0:
            #   break
              
            # self.__dp[i][j] = 1
            j = update_fnc(j)

        # j is either end pos 
        # or j where self.img[i][j] != BG 
        # or part of outer region
        return j

    def __findInterval(self, i, j):
        # find the interval where pixels is BG
        isBG = lambda v: v == self.__BG_PIXELS_INTENSITY
        
        j_start = self.__sweep(i, j - 1, lambda x: x - 1, isBG, -1) + 1
        j_end = self.__sweep(i, j + 1, lambda x: x + 1, isBG, self.nx) - 1
        
        return (j_start, j_end)

    def __fill(self, stack):
        # count region total in stack
        region_count = 0

        while len(stack) > 0:
            # if region is connected to outer region, don't count
            # if region is already visited, stop the search
            data = stack.pop(0)
            i_start, (j_start, j_end) = data

            if self.__dp[i_start][j_start] != 0:
                continue

            region_count += 1  # add region
            i_start += 1
            
            # scan left then move the cursor down
            while i_start < self.ny:
                # find entry point
                j_entry = -1
                for j_ in range(max(j_start - 1, 0), min(j_end + 2, self.nx)):
                  if self.img[i_start][j_] == self.__BG_PIXELS_INTENSITY:
                    j_entry = j_
                    break
                  
                if j_entry == -1:
                  break

                j_start_curr, j_end_curr = self.__findInterval(i_start, j_entry)
                
                # region is terminated
                if j_start_curr > j_end + 1:
                  break
                
                if j_end_curr < j_start - 1:
                  break
                
                
                # check if region is connected to outer region
                # part of other region
                if self.__checkOtherRegion(i_start, j_start_curr) or self.__checkOtherRegion(i_start, j_end_curr):
                  region_count -= 1
                  break
                
                # region is connected
                for j_ in range(j_start_curr, j_end_curr + 1):
                  self.__dp[i_start][j_] = 1
                  
                if j_end_curr == self.nx - 1 or j_start_curr == 0:
                  region_count -= 1
                  break
                
                
                j_start = j_start_curr
                j_end = j_end_curr
                
                  
                i_start += 1
                
        return region_count

    def __existUpper(self, i, j):
      for k in range(-1, 2):
        if j + k >= self.nx or j + k < 0:
          continue
        
        if self.img[i - 1][j + k] == self.__BG_PIXELS_INTENSITY:
          return True
      return False
    
    def loop_count(self):
        stack = []
        for i in range(self.ny):
            j = 0
            while j < self.nx:
                self.__dp[i][j] = -1
                if self.img[i][j] != self.__BG_PIXELS_INTENSITY:
                    jr = j  # j start region
                    if i - 1 < 0:
                        break
                    # start of a new region 
                    isExistUpper  = False
                    while jr < self.nx and self.img[i][jr] != self.__BG_PIXELS_INTENSITY:
                        jr += 1

                    jsr = jr  # j stop region
                    while jsr < self.nx and self.img[i][jsr] == self.__BG_PIXELS_INTENSITY:
                        if self.__existUpper(i, jsr):
                          isExistUpper = True
                        self.__dp
                        jsr += 1
                        
                    if jsr == self.nx:
                        break

                    # region not connected to outer region
                    # and not connected to other region
                    if not isExistUpper:
                      stack.append([i, (jr, jsr - 1)])
                    
                    if len(stack) > 1 and isExistUpper and stack[-1][0] == i:
                      stack.append([i, (jr, jsr)])
                    
                    j = jsr

                else:
                    j += 1

        return self.__fill(stack)
      



      

    
    