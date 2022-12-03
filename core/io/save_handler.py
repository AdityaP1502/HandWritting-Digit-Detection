from PIL import Image
import numpy as np

from core.io.path_handler import PathHandler
import conf.conf as conf

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
        
    def save_results(filenames, results):
        # results is a list consisting of file and its detected value
        path = PathHandler.make_path("EXPORT", conf.EXPORT_FILENAME, "SAVE")
        contents = []
        with open(path, "w") as f:
            for (file, detected_val) in zip(filenames, results):
                content = "{}\n".format(file)
                content += ",".join(list(map(lambda x: str(x), detected_val)))
                contents.append(content)

            contents_str = "\n".join(contents)
            f.write(contents_str)
                
                
