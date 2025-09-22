from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import multiprocessing
import os

from utils.io_utils import print_progress


class Annotation:
    def __init__(self, annotation_file_path):
        self.annotation_file_path = os.path.normpath(annotation_file_path)
        assert os.path.exists(self.annotation_file_path)

    def save_to_file(self, save_path, author, len_check, frames_per_second):
        with open(filename, "w") as f:
            f.write(f'author:§{author}§ lenght:§{len_check}§ fps:§{frames_per_second}§\n')

    def update_annotation_scale(self, filename, new_filename, scale=4):
        """
        NOT SURE FOR WHAT THIS IS USED
        :param filename:
        :return:
        """

        with open(filename, "r") as f:
            for line in f[1:]:

                if '.' in line:
                    class_id, x1, y1, x2, y2 = line.split(' ')
                    bbox = [float(x1) / scale, float(y1) / scale, float(x2) / scale, float(y2) / scale]

                    with open(new_filename, "a") as f:
                        f.write(f'{class_id} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n')
                elif len(line) is 0:
                    # eof
                    break
                else:
                    # frame number lines
                    with open(newFile, "a") as f:
                        f.write('{}\n'.format(int(line)))