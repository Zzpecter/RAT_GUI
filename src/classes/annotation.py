from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import multiprocessing
import os

from utils.io_utils import print_progress


class Annotation:
    def __init__(self, annotation_file_path):
        self.annotation_file_path = os.path.normpath(annotation_file_path)
        assert os.path.exists(self.annotation_file_path)
        self.ann_dict = {}
        self.author = None
        self.ann_count = None
        self.fps = None
        self.load_from_file()

    def load_from_file(self):
        current_frame = None
        with open(self.annotation_file_path) as file:
            while line := file.readline():
                if 'author' in line:
                    header_items = line.split('§')
                    self.author = header_items[1]
                    self.ann_count = header_items[3]
                    self.fps = header_items[5]
                elif all([d.isdigit() for d in line.strip()]):
                    current_frame = int(line.strip())
                elif len(line.split(' ')) == 5: # bbox line
                    if current_frame is None:
                        print(f'error in line {line} current_frame is none')
                        continue
                    if self.ann_dict.get(current_frame, None) is None:
                        self.ann_dict[current_frame] = []
                    self.ann_dict[current_frame].append([int(e) for e in line.split(' ')])


    def save_to_file(self, , author, len_check, frames_per_second):
        with open(self.annotation_file_path, "w") as f:
            f.write(f'author:§{self.author}§ lenght:§{self.len_check}§ fps:§{self.frames_per_second}§\n')

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