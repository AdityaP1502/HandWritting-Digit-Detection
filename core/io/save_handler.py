from PIL import Image
import numpy as np
from core.io.path_handler import PathHandler


class SaveHandler():
    @staticmethod
    def save_image(img, filename):
        assert isinstance(img, np.ndarray), "Image must be an numpy ndarray, get {}".format(
            type(img).__name__)
        assert len(
            np.shape(img)) >= 2, "Invalid Image size. Image must be a matrix"

        path = PathHandler.make_path("IMAGE", filename, "SAVE")
        saved_img = Image.fromarray(img, mode="L")
        saved_img.save(path, mode="L")
