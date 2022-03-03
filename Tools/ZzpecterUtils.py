import cv2
import os
from PIL import Image

#Loads a Video with openCV, reads frame by frame and saves them in ./Data/VideoName/Frames/
#args:
# - videoPath: string representing the path for the selected video
# - videoName: string representing the name and extension of the selected video
# - doResize: bool representing wether the video frames should stay in original shape or resized. def: FALSE
# - shape(width, height): tuple representing the shape of the resized frames. def:(640,480)
#returns:
# - frames: List consisting of all video frames
# - resFrames: List consisting of the resized video frames
def GenerateVideoFrames(videoPath, videoName, doResize = False, shape = (640,480)):

    frames = []
    resFrames = []

    #cropping the extension out
    videoNameCrop = ""
    i = 0
    while videoName[i] != '.':
        videoNameCrop += videoName[i]
        i += 1

    #Create a new folder for the video
    frameFolder = "./Data/{}/".format(videoNameCrop)
    if not os.path.exists(newpath):
        os.makedirs(frameFolder)

    #Save the frames, TODO: copy the video file itself
    vidcap = cv2.VideoCapture("{}{}".format(videoPath, videoName))
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

    frames = []
    resFrames = []

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
