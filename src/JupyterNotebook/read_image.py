import cv2
def read_images(path):
    a = cv2.imread(path, 0)   
    return a