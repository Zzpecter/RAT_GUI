import cv2
import numpy as np
import os
from random import randint

def getNbr(number):
    number = str(number)
    while(len(number)<12):
        number = "0{}".format(number)
    return number

def getOFMask(imagePath = './Projects/FRA 19 SHD POV LOE/images/', sample = 0.01, filterThresh = 0.08):
    filterThresh = int(filterThresh * 255)
    numF = len([name for name in os.listdir(imagePath)])
    testLenght = int(numF * sample) #1% test lenght by default
    filterSum = np.zeros(shape = (540,960), dtype=np.float32)

    for i in range(0, testLenght):
        r = randint(1, numF-1)
        file = '{}.jpg'.format(getNbr(r))
        nFile = '{}.jpg'.format(getNbr(r+1))

        im1 = cv2.cvtColor( cv2.imread( os.path.join( imagePath, file )), cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor( cv2.imread( os.path.join( imagePath, nFile )), cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(im1, im2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        gray = np.zeros((flow.shape[0], flow.shape[1]), np.float32)#Converting only the magnitude of OF to grayscale image
        gray = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        filterSum += gray

        
    filterSum /= int(numF * sample)#normalize on sample length
    # loop over the image
    for y in range(0, 540):
        for x in range(0, 960):
            # threshold the pixel
            filterSum[y, x] = 255 if filterSum[y, x] >= filterThresh else 0

    cv2.imwrite('{}rawFilter.png'.format(imagePath), filterSum)
    cv2.imshow('raw Optical Flow mask', filterSum)
    cv2.waitKey(0)
    #Added erosion + dilation to smooth the filters shape
    kernel = np.ones((13,13), np.uint8) #Tested various filter sizes, as the images have relatively high res, 13 performs good.
    erodedImg = cv2.erode(filterSum, kernel, iterations=3) # 3 iters 
    filterSum = cv2.dilate(erodedImg, kernel, iterations=1) 
    cv2.imwrite('{}filter.png'.format(imagePath), filterSum)

    r = randint(1, numF-1)
    file = '{}.jpg'.format(getNbr(r))
    originalFrame = cv2.imread( os.path.join( imagePath, file ))
    filterSum = filterSum.astype(np.uint8)

    res = cv2.bitwise_and(originalFrame,originalFrame,mask = filterSum) #a lot more effective than my c-way of applying the mask

    filtered = 0 
    for n in np.reshape(filterSum, [-1]):
        if n == 0:
            filtered += 1

    print ('Filtering Ratio: {}'.format(filtered/(960*540)))
    
    cv2.imshow('smoothed mask applied to img', res)
    cv2.waitKey(0)

if __name__ == '__main__':
    getOFMask()