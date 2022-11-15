from ctypes import *
from os.path import abspath
import numpy as np
SO_DIRPATH = "src/libs/"

# Struct
class Image(Structure):
  _fields_ = [
    ("img", POINTER(c_ubyte)), 
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

# BBOX
SO_FILE_BBOX = SO_DIRPATH + 'libbbox.so'
bbox_c = CDLL(SO_FILE_BBOX)
bbox_c.python_bbox_find.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
bbox_c.python_bbox_find.restype = POINTER(Data)

# Thresh
SO_FILE_THRESH = SO_DIRPATH + 'libthresh.so'
thresh_c = CDLL(SO_FILE_THRESH)
thresh_c.python_thresh_images.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int, c_ubyte, c_ubyte]
thresh_c.python_thresh_images.restype = POINTER(Image)

# Image To Serial and Serial To Images
SO_FILE_IMAGES = SO_DIRPATH + 'libimage.so'
image_c = CDLL(SO_FILE_IMAGES)
image_c.image_to_serial.argtypes = [POINTER(POINTER(c_ubyte)), c_int, c_int]
image_c.image_to_serial.restype = POINTER(c_ubyte)
image_c.serial_to_image.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
image_c.serial_to_image.restype = POINTER(POINTER(c_ubyte))

# Loop Counter
SO_FILE_COUNTER = SO_DIRPATH + 'libcounter.so'
counter_c = CDLL(SO_FILE_COUNTER)
counter_c.python_loop_count.argtypes = [np.ctypeslib.ndpointer(dtype=c_ubyte, flags="C_CONTIGUOUS"), c_int, c_int]
counter_c.python_loop_count.restypes = c_int

def serializeArray_c(pixels, nx, ny):
    pixels_ptr = POINTER(c_ubyte) * ny
    temp = []
    for i in range(ny):
        temp.append(cast(np.ctypeslib.as_ctypes(pixels[i]), POINTER(c_ubyte)))
    
    pixels_ptr = cast(pixels_ptr(*temp), POINTER(POINTER(c_ubyte)))
    
    data_ptr = image_c.image_to_serial(pixels_ptr, nx, ny)
    return np.ctypeslib.as_array(data_ptr, (nx * ny,))

def toMatrix(serial, nx, ny):
    shape = np.shape(serial)
    if not isinstance(serial, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(serial).__name__))
    assert (len(shape) == 1), "Image must be serialized"
    
    try:
        data_ptr = image_c.serial_to_image(serial, nx, ny)
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined image_c. Make sure to load image_c library first before running this function\n")
        print("Make sure to defined the restype and argtype of serial_to_image")
        exit(-1)
    
    mat = [None for i in range(ny)]
    for i in range(ny):
        mat[i] = np.ctypeslib.as_array(data_ptr[i] ,shape=(nx,))
    return np.array(mat)
    
    
def bbox_pipeline(img : np.ndarray, nx, ny):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 1), "Image must be serialized"

    #pixels_serialize = serializeArray(img, nx, ny)
  
    try:
        data_ptr = bbox_c.python_bbox_find(img, nx, ny)
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
    #plt.show()

def thresh_pipeline(img, nx, ny, thresh):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 1), "Image must be serialized"
  
    #pixels_serialize = serializeArray(img, nx, ny)
    try:
        data_ptr = thresh_c.python_thresh_images(img, nx, ny, 0, thresh)
        
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined bbox. Make sure to load thresh library first before running this function\n")
        print("Make sure to defined the restype and argtype of python_thresh_images")
        exit(-1)
    
    data : Image = data_ptr.contents
    thresh_images = np.ctypeslib.as_array(data.img, (data.ny * data.nx,))
    return thresh_images

def loop_count_c(img, nx, ny):
    shape = np.shape(img)
    if not isinstance(img, np.ndarray): 
        raise TypeError("Image must be a ndarray, get {}".format(type(img).__name__))
    assert (len(shape) == 1), "Image must be serialized"
    
    try:
        cnt = counter_c.python_loop_count(img, nx, ny)
    except Exception as e:
        print("Exception occured: {}".format(e))
        print("If error caused by undefined counter. Make sure to load counter_c library first before running this function\n")
        print("Make sure to defined the restype and argtype of python_loop_count")
        exit(-1)
        
    return cnt
