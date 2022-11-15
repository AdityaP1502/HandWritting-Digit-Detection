import numpy as np
import cv2
import scipy.ndimage as sciim
from os.path import abspath
from c_interface import serializeArray_c, loop_count_c

IMG_DIRPATH_DEFAULT = abspath("img/")
class Images():
    def __init__(self, filename) -> None:
        self.pixels = cv2.imread(filename)
        self.backup = None

    def toGrayscale(self):
      self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
      
    def accentPicture(self, iterations=1):
      self.pixels = cv2.erode(self.pixels, np.ones((7,7), np.uint8), iterations=iterations)

    def doBackup(self):
      self.backup = np.copy(self.pixels)

    def restart(self):
      self.pixels = np.copy(self.backup)

class ShadowRemoval():
  def __init__(self, img):
    self.img = img
    self.kernel = np.ones((7, 7), np.uint8)
    self.output = None

  def remove(self):
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
  
def shiftImage(img, shift):
    dst = sciim.shift(img, shift, cval=255)
    dst = dst.astype('ubyte')
    return dst

def scaleImage(img):
    dim = (28, 28)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_CUBIC)
    return resized

def centerImage(img):
    # create an image with 1 : 1 aspect ratio
    ny, nx = np.shape(img)
    dim = max(nx, ny)
    a = np.full((dim, dim), 255)
    
    for i in range(ny):
        for j in range(nx):
            a[i][j] = img[i][j]
    
    # shift image so the shape in the center
    dx = (dim - nx) / 2
    dy = (dim - ny) / 2
    return shiftImage(a, (dy, dx))

def filteredImages(shapes, frames, filteredFrames):
    start_i, start_j = frames[0]
    exclude = [[0, 0], [0, 0]]
    exclude[0][0] = max(filteredFrames[0][0], frames[0][0])
    exclude[0][1] = max(filteredFrames[0][1], frames[0][1])
    exclude[1][0] = min(filteredFrames[1][0], frames[1][0])
    exclude[1][1] = min(filteredFrames[1][1], frames[1][1])
    for i_ in range(exclude[0][0], exclude[1][0] + 1):
            for j_ in range(exclude[0][1], exclude[1][1] + 1):
                shapes[i_ - start_i][j_ - start_j] = 255

def getShape(x, partition, k):
    # partition is sorted based on min_j
    obj = partition[k]
    [min_i, min_j], [max_i, max_j] = obj
    py = (max_i - min_i) + 1
    px = (max_j - min_j) + 1
    
    shape = np.zeros((py, px))
    
    start_i = min_i
    start_j = min_j
    # find other images from partition that exist in current frames
    # find images with  frames_min_j < min_j < frames_max_j
    # therefore only need to check next images                                   
    for i in range(py):
        for j in range(px):
            shape[i][j] = x[start_i + i][start_j + j]
    
    # remove any overlap object in current frames
    lo = k - 1
    while (lo >= 0 and partition[lo][1][1] > min_j):
        filteredImages(shape, obj, partition[lo])
        lo -= 1
    
    hi = k + 1
    while (hi < len(partition) and partition[hi][0][1] < max_j):
        filteredImages(shape, obj, partition[hi])
        hi += 1                                    
    
    return scaleImage(centerImage(shape))

def pipeline(data):
    img, partition, j = data
    shape = getShape(img, partition, j)
    shape_erode = cv2.erode(shape, np.ones((3, 3), np.uint8))
    shape_erode = serializeArray_c(shape_erode, 28, 28)
    # add lopp count features
    cnt = loop_count_c(shape_erode, 28, 28)
    return np.append(shape_erode, cnt)