import cv2
import numpy as np
import scipy.ndimage as sciim

import conf.conf as conf
from core.CDLL.c_interface import *

class ImageOperator():
    @staticmethod
    def shadow_remove(img):
        rgb_planes = cv2.split(img)
        result_norm_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((11, 11), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(
                diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_norm_planes.append(norm_img)
        shadowremov = cv2.merge(result_norm_planes)
        return shadowremov

    @staticmethod
    def thresh_images(img, nx, ny, thresh):
      thresh_image_c(img, nx, ny, thresh)
      
    @staticmethod
    def find_bbox(img, nx, ny):
        return bbox_find_c(img, nx, ny)

    @staticmethod
    def loop_enhance(img, nx, ny):
        return loop_enhance_c(img, nx, ny)

    @staticmethod
    def object_detect(img, nx, ny):
        def get_partitions():
            partitions = []
            objs.sort(key=lambda x: x[0][0])  # sort based on min_i value
            upper = objs[0][1][0]
            start = 0
            for i in range(1, len(objs)):
                if objs[i][0][0] < upper:
                    upper = objs[i][1][0]
                    continue

                upper = objs[i][1][0]
                partitions.append(objs[start: i])
                start = i

            # edge cases
            partitions.append(objs[start: len(objs)])
            return partitions

        def sortObjs():
            partitions = get_partitions()
            for partition in partitions:
                partition.sort(key=lambda x: x[0][1])  # sort based on min
            return partitions

        objs = ImageOperator.find_bbox(img, nx, ny)
        return sortObjs()

    @staticmethod
    def remove_overlap(shapes, frames, overlap_frames):
        start_i, start_j = frames[0]
        exclude = [[0, 0], [0, 0]]
        exclude[0][0] = max(overlap_frames[0][0], frames[0][0])
        exclude[0][1] = max(overlap_frames[0][1], frames[0][1])
        exclude[1][0] = min(overlap_frames[1][0], frames[1][0])
        exclude[1][1] = min(overlap_frames[1][1], frames[1][1])
        for i_ in range(exclude[0][0], exclude[1][0] + 1):
            for j_ in range(exclude[0][1], exclude[1][1] + 1):
                shapes[i_ - start_i][j_ - start_j] = 255

    @staticmethod
    def to_serial(img, nx, ny):
      return serialize_array_c(img, nx, ny)
        

    @staticmethod
    def to_matrix(img, nx, ny):
        return to_matrix_c(img, nx, ny)

    @staticmethod
    def shift_image(img, shift):
        dst = sciim.shift(img, shift, cval=conf.BG_PIXELS_INTENSITY)
        dst = dst.astype('ubyte')
        return dst

    @staticmethod
    def scale_image(img):
        dim = (28, 28)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        return np.array(resized)

    @staticmethod
    def center_image(img):
        # create an image with 1 : 1 aspect ratio
        ny, nx = np.shape(img)
        dim = max(nx, ny)
        dim += dim % 2
        dim = int(1.5 * dim)

        if conf.BG_PIXELS_INTENSITY == 0:
            a = np.zeros((dim, dim))

        else:
            a = np.full((dim, dim), 255)

        for i in range(ny):
            for j in range(nx):
                a[i][j] = img[i][j]

        # shift image so the shape in the center
        dx = (dim - nx) / 2
        dy = (dim - ny) / 2
        return ImageOperator.shift_image(a, (dy, dx))

    @staticmethod
    def to_grayscale(img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def remove_noise(img):
        se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
        bg = cv2.morphologyEx(img, cv2.MORPH_DILATE, se)
        out = cv2.divide(img, bg, scale=255)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        out_cleaned = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel)
        return out_cleaned

    @staticmethod
    def close_image(pixels_serial, nx, ny):
        img = ImageOperator.to_matrix(pixels_serial, nx, ny)
        img_clean = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((3, 3)))
        return ImageOperator.to_serial(img_clean, nx, ny)
      
    def accent_white(pixels, n_iter=1):
        return cv2.dilate(pixels, np.ones((3, 3)), iterations=n_iter)
