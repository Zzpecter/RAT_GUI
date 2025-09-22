import cv2
import os
from PIL import Image
#
# videoPath = './videos/FRA 19 SHD POV LAP.mp4'
# frameDir = './extractedFrames1920/FRA19LAP/'




def extract_frames(video_path, video_filename, resize = False, new_shape = (640,480)):

    frames = []
    resFrames = []


    #Create a new folder for the video
    project_path = f"./Projects/{video_filename.strip('.mp4')}/"
    frame_path = project_path + "frames/"
    os.makedirs(project_path, exist_ok=True)
    os.makedirs(frame_path, exist_ok=True)

    # TODO: copy the video file itself
    vidcap = cv2.VideoCapture("{}{}".format(video_path, video_filename))
    success,image = vidcap.read()
    i = 0
    while success:
        frames.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        #Normalizing the filename lenght to 12, to get proper ordering for videos up to 999.999.999.999 frames long.
        number = str(i)
        while(len(number)<12):
            number = "0{}".format(number)

        name = "{}{}.jpeg".format(frameFolder,number)
        image.save(name)
        success,image = vidcap.read()

    #TODO: is it not better to have an extra function for resizing???
    if doResize:
        for frame in frames:
            resFrames.append(imresize(frame, shape))


    return frames, resFrames

def GetVideoFrames(videoPath, videoName, doResize = False, shape = (640,480)):


    vidcap = cv2.VideoCapture(videoUrl)
    success,image = vidcap.read()
    while success:
        frames.append(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image.save("./Data/Frames/frame{}.jpeg".format(i))
        success,image = vidcap.read()

    if doResize:
        for frame in frames:
            resFrames.append(imresize(frame, (yoloModel.width, yoloModel.height)))


    return frames, resFrames



