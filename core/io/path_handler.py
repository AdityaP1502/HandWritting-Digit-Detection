import os
import os.path
import conf.conf as conf


class PathHandler():
    @staticmethod
    def make_path(filetype: str, filename: str, mode: str) -> str:
        """Create a path to save/load a file

        Args:
            filetype(str): file type. Available option are IMAGE and MODEL
            filename (str): filename
            mode (str): accepted mode is SAVE or LOAD for IMAGE and LOAD for model

        Returns:
            str: path to save/load a file
        """

        mode = mode.upper()

        if mode == "LOAD":
            if filetype == "IMAGE":
                return os.path.join(conf.IMG_DIRPATH, filename)

            elif filetype == "MODEL":
                return os.path.join(conf.MODELS_DIR, filename)

            else:
                raise ValueError(
                    "Cannot process {} filetype. Filetype not supported".format(filetype))

        elif mode == "SAVE":
            if filetype == "IMAGE":
                return os.path.join(conf.DEBUG_OUT_PATH, filename)

            elif filetype == "MODEL":
                raise ValueError(
                    "Cannot save file with filetype {}".format("MODEL"))

            else:
                raise ValueError(
                    "Cannot process {} filetype. Filetype not supported".format(filetype))

        else:
            raise ValueError(
                "Cannot process {} mode. Argument not supported".format(mode))

    @staticmethod
    def check_path(path: str, not_exist_create: bool = False) -> bool:
        """Check if a given path exist or not. If not_exist create is set, then will create a new directory

        Args:
            path (str): path
            not_exist_create (bool, optional): create new directory if not exist. Defaults to False.

        Returns:
            bool: return if path exist. If not_exist_create is set, output will always be true
        """

        is_exist = os.path.isdir(path)

        if (not is_exist and not_exist_create):
            os.makedirs(path)
            return True

        return is_exist

    @staticmethod
    def check_file(filename: str, file_must_exist=True) -> bool:
        """Check if a file exist. 

        Args:
            filename (str): filename. Assumed location at LOAD location
            file_must_exist (bool, optional): if file_must_exist is set to true, would raise a FileNotFoundError. Defaults to True.

        Returns:
            bool: _description_
        """

        path = PathHandler.make_path("IMAGE", filename, "LOAD")
        is_exist = os.path.isfile(path)

        if not is_exist and file_must_exist:
            raise FileNotFoundError("File in {} doesn't exist".filepath)

        return is_exist

    @staticmethod
    def list_image():
        dir_list = os.listdir(conf.IMG_DIRPATH)
        extension = list(map(lambda x: x.split(".")[-1], dir_list))
        img_list = [file for (i, file) in enumerate(
            dir_list) if extension[i] == 'jpg' or extension[i] == 'png']
        return img_list
