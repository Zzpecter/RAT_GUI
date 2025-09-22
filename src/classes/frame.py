import cv2
import os


class Frame:
    def __init__(self, index, img_path, resize_shape=None):
        self.index = index
        self.img_path = os.path.normpath(img_path)
        assert os.path.exists(self.img_path)

        self.image = cv2.cvtColor(cv2.imread(self.img_path), cv2.COLOR_BGR2RGB)
        if isinstance(resize_shape, tuple):
            # TODO: resize
            pass
