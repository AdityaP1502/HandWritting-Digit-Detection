import numpy as np


class PixelAnalyzer():
    MAXIMUM_BLACK_PIXEL = 200  # maximum pixel value that can be considered as black

    """
  Class to analyze pixel distribution from a image
  """
    @staticmethod
    def fromPixelsToHistogram(img):
        """Generate pixel distribution using histogram

        Args:
            img (np.array): Images in array form(serialize)

        Returns:
           np.array : 1D array of pixel density from 0 - 255
        """
        x = np.array([0 for i in range(0, 256)])

        shape = np.shape(img)
        assert len(shape) == 1, "Image must be serial"

        for pix_val in img:
            x[pix_val] += 1
        window = 21
        order = 2

        from scipy.signal import savgol_filter
        x_smoothen = savgol_filter(x, window, order)
        x_smoothen[x_smoothen < 0] = 0
        x_smoothen /= len(img)
        return np.round(x_smoothen, 5)

    @classmethod
    def __findPeak(cls, x):
        # just find the maximum value between 0 - 200
        peak = [0, 0]
        for i in range(cls.MAXIMUM_BLACK_PIXEL):
            if peak[1] < x[i]:
                peak = [i, x[i]]
        return peak

    @classmethod
    def __findValley(cls, X, peak_idx):
        valley = 1
        for i in range(peak_idx, cls.MAXIMUM_BLACK_PIXEL + 1):
            valley = min(valley, X[i])

        # find the digit of valley
        digit = 0
        mult = 1
        temp = valley

        while temp < 1:
            temp *= 10
            mult *= 10
            digit += 1

        return valley, mult, digit

    @classmethod
    def findThreshold(cls, img) -> int:
        """Find threshold value from a given image. Threshold is the maximum value
        of data pixels. Any value greater than threshold would be considered as background

        Args:
            img (np.ndarray): img in 1D array 

        Returns:
           int: threshold value (max_threshold)
        """

        X = cls.fromPixelsToHistogram(img)
        peak = cls.__findPeak(X)
        i = peak[0]
        valley, mult, digit = cls.__findValley(X, i)
        thresh_val = round(valley + (1 / mult), digit)
        
        thresh = cls.MAXIMUM_BLACK_PIXEL
        
        for i in range(i + 1, cls.MAXIMUM_BLACK_PIXEL + 1):
            if X[i - 1] >= X[i] and X[i + 1] > X[i]:
                if X[i] <= thresh_val:
                    thresh = i
            i += 1

        return thresh
