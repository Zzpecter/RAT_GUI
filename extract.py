import os

videoPath = './videos/FRA 19 SHD POV LAP.mp4'
frameDir = './extractedFrames1920/FRA19LAP/'

os.system('ffmpeg -i "{}" -qscale:v 2 "{}"%12d.jpg'.format(videoPath, frameDir))




