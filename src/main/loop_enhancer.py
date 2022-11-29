import numpy as np
from os.path import abspath
from ctypes import *


class LoopEnhancer():
    __BG_PIXELS_INTENSITY = 0
    __DATA_LOOP_INTENSITY = 255
    __DATA_INTENSITY = 150
    __MAX_COUNT = 2

    def __init__(self, img) -> None:
        ny, nx = np.shape(img)
        self.img = img
        self.ny = ny
        self.nx = nx
        self.__dp = [[0 for j in range(nx)] for i in range(ny)]

    def __checkOtherRegion(self, i, j):
        return (self.__dp[i][j] != 0)

    def __sweep(self, i, j, update_fnc, condition_fnc, end_pos, label):
        while j != end_pos and condition_fnc(self.img[i][j]):
            if self.__checkOtherRegion(i, j):
                break
            
            if label:
              self.__dp[i][j] = 1
              
            # if self.dp[i][j] != 0:
            #   break

            # self.__dp[i][j] = 1
            j = update_fnc(j)

        # j is either end pos
        # or j where self.img[i][j] != BG
        # or part of outer region
        return j
      
    def __isBG(self, v):
      return v == self.__BG_PIXELS_INTENSITY
    
    def __isNotBG(self, v):
      return v != self.__BG_PIXELS_INTENSITY
    
    def __findInterval(self, i, j, mode = "BG", label=False):
        # find the interval where pixels is BG
        if mode == "BG":
          fnc = self.__isBG
          
        elif mode == "DATA":
          fnc = self.__isNotBG

        if label:
          self.__dp[i][j] = 1
          
        j_start = self.__sweep(i, j - 1, lambda x: x - 1, fnc, -1, label) + 1
        j_end = self.__sweep(i, j + 1, lambda x: x + 1, fnc, self.nx, label) - 1

        return (j_start, j_end)

    def __label_outer(self, i_start, fnc, end_pos, j_entry):
        cnt = 0
        i = fnc(i_start)
        j = j_entry
        while self.img[i][j] != self.__BG_PIXELS_INTENSITY:
          self.__dp[i][j] = 1
          j -= 1  
        j_start = j + 1
        
        j = j_entry
        while self.img[i][j] != self.__BG_PIXELS_INTENSITY:
          self.__dp[i][j] = 1
          j += 1
        j_end = j - 1
        
        i = fnc(i)
        while i  != end_pos:
          j_entry = -1
          for j_ in range(max(j_start, 0), min(j_end + 1, self.nx)):
              if self.img[i][j_] != self.__BG_PIXELS_INTENSITY:
                  j_entry = j_
                  break
                
          # region is terminated
          if j_entry == -1:
              break
            
          j_start_curr, j_end_curr = self.__findInterval(i, j_entry, mode = "DATA", label = True)
          if j_start == j_start_curr and j_end == j_end_curr:
            cnt += 1
            
          if cnt > self.__MAX_COUNT:
            break
          
          j_start = j_start_curr
          j_end = j_end_curr
          
          i = fnc(i)
          

            

    def __label_inner(self, i, j_start, j_end):
        j = j_start - 1
        while self.img[i][j] != self.__BG_PIXELS_INTENSITY:
            self.__dp[i][j] = 1
            j -= 1

        j = j_end + 1
        while self.img[i][j] != self.__BG_PIXELS_INTENSITY:
            self.__dp[i][j] = 1
            j += 1
            
        

    def __fill(self, stack):
        # label loop pixels
        while len(stack) > 0:
            # if region is connected to outer region, don't count
            # if region is already visited, stop the search
            data = stack.pop(0)
            i_start, (j_start, j_end) = data
            i_min = i_start
            temp = j_start
            frames = []
            frames.append([i_start, j_start, j_end])

            if self.__dp[i_start][j_start] != 0:
                continue

            isUnique = True
            i_start += 1

            # scan left then move the cursor down
            while i_start < self.ny:
                # find entry point
                j_entry = -1
                for j_ in range(max(j_start - 1, 0), min(j_end + 2, self.nx)):
                    if self.img[i_start][j_] == self.__BG_PIXELS_INTENSITY:
                        j_entry = j_
                        break

                # region is terminated
                if j_entry == -1:
                    break

                j_start_curr, j_end_curr = self.__findInterval(i_start, j_entry)

                # if j_start_curr > j_end + 1:
                #   break

                # if j_end_curr < j_start - 1:
                #   break

                # check if region is connected to outer region
                # part of other region
                if self.__checkOtherRegion(i_start, j_start_curr) or self.__checkOtherRegion(i_start, j_end_curr):
                    isUnique = False
                    break

                # region is connected
                for j_ in range(j_start_curr, j_end_curr + 1):
                    self.__dp[i_start][j_] = 1

                if j_end_curr == self.nx - 1 or j_start_curr == 0:
                    isUnique = False
                    break

                j_start = j_start_curr
                j_end = j_end_curr
                frames.append([i_start, j_start, j_end])

                i_start += 1

            i_end = i_start - 1
            if isUnique:
                for frame_pos in frames:
                    self.__label_inner(*frame_pos)
                    self.__label_outer(i_min, lambda x: x - 1, -1, temp)
                    self.__label_outer(i_end, lambda x: x + 1, self.ny, temp)

    def __existUpper(self, i, j):
        for k in range(-1, 2):
            if j + k >= self.nx or j + k < 0:
                continue

            if self.img[i - 1][j + k] == self.__BG_PIXELS_INTENSITY:
                return True

        return False

    def __init_stack(self):
        stack = []
        for i in range(self.ny):
            j = 0
            while j < self.nx:
                if self.img[i][j] != self.__BG_PIXELS_INTENSITY:
                    jr = j  # j start region
                    if i - 1 < 0:
                        break
                    # start of a new region
                    isExistUpper = False
                    while jr < self.nx and self.img[i][jr] != self.__BG_PIXELS_INTENSITY:
                        jr += 1

                    jsr = jr  # j stop region
                    while jsr < self.nx and self.img[i][jsr] == self.__BG_PIXELS_INTENSITY:
                        if self.__existUpper(i, jsr):
                            isExistUpper = True
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
                    self.__dp[i][j] = -1
                    j += 1

        return stack

    def enhance(self):
        stack = self.__init_stack()
        self.__fill(stack)
        for i in range(self.ny):
            for j in range(self.nx):
                if self.img[i][j] != self.__BG_PIXELS_INTENSITY:

                    if self.__dp[i][j] != 1:
                        self.img[i][j] = self.__DATA_INTENSITY

                    else:
                        self.img[i][j] = self.__DATA_LOOP_INTENSITY
