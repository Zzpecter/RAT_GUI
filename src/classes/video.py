from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import multiprocessing
import os

from utils.io_utils import print_progress

# TODO: see if this could be a backup function
# def extract_frames(video_file_path, target_dir_name):
#     os.system(f'ffmpeg -i "{video_file_path}" -qscale:v 2 "{target_dir_name}"%12d.jpg')
#

class Video:
    def __init__(self,
                 video_path,
                 video_filename,
                 frame_save_dir,
                 chunk_size=5,
                 overwrite=False,
                 frame_extraction_interval=1):
        self.video_path = os.path.normpath(video_path)
        assert os.path.exists(self.video_path)
        self.video_dir, _ = os.path.split(self.video_path)
        self.video_filename = os.path.normpath(video_filename)
        self.frame_save_dir = os.path.normpath(frame_save_dir)
        self.chunk_size = chunk_size
        self.overwrite = overwrite
        self.frame_extraction_interval = frame_extraction_interval

    def extract_and_save_frames(self):
        capture = cv2.VideoCapture(self.video_path)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        capture.release()

        frame_chunks = [[i, i + self.chunk_size] for i in range(0, frame_count, self.chunk_size)]
        frame_chunks[-1][-1] = min(frame_chunks[-1][-1], frame_count - 1)
        prefix_str = f"Extracting frames from {self.video_filename}"

        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:

            futures = [executor.submit(self.extract_frame_chunk, f[0], f[1]) for f in frame_chunks]

            for i, f in enumerate(as_completed(futures)):
                print_progress(i, len(frame_chunks)-1, prefix=prefix_str, suffix='Complete')

    def extract_frame_chunk(self, start=-1, end=-1):
        capture = cv2.VideoCapture(self.video_path)

        if start < 0:
            start = 0
        if end < 0:
            end = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        capture.set(1, start)
        frame = start
        frames_saved = 0

        while frame < end:
            _, image = capture.read()

            if image is None:
                continue
            if frame % self.frame_extraction_interval == 0:
                save_path = os.path.join(self.frame_save_dir,
                                         self.video_filename,
                                         "{:010d}.jpg".format(frame))
                if not os.path.exists(save_path) or self.overwrite:
                    cv2.imwrite(save_path, image)
                    frames_saved += 1
            frame += 1
        capture.release()

        return frames_saved
