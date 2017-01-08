import argparse
import os
import time

import numpy as np
from PIL import Image
from pymba import *


def capture_image(frame, channels=3, frame_wait=2000):
    """
    Captures one frame and converts it to a numpy array
    :param frame_wait: Time in miliseconds to give camera in order to process acquired image
    :param frame: Frame object
    :param channels: Color Depth
    :return: Image data in a numpy array of shape (height, width, channels)
    """
    frame.waitFrameCapture(timeout=frame_wait)

    img_data = frame.getBufferByteData()
    data = np.ndarray(buffer=img_data,
                      dtype=np.uint8,
                      shape=(frame.width,
                             frame.height,
                             channels))
    # clean up after capture
    frame.queueFrameCapture()
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--frequency", action="store", default=5, help="Capture frequency")
    parser.add_argument("-d", "--directory", action="store",
                        help="Save Directory")
    parser.add_argument("-n", "--img_num", action="store",
                        help="Number of images to capture. Negative value will capture until the user quits the program",
                        type=int, default=1)
    parser.add_argument("-p", "--prefix", action="store",
                        help="Image filenames prefix", default="img_")
    parser.add_argument("-e", "--exposure", action="store", type=float,
                        help="Exposure Time. Minimum: 26, Maximum: 60000000", default=2000000.0)
    parser.add_argument("-g", "--gamma", action="store", type=float,
                        help="Gamma value. Minimum: 0.45, Maximum: 1", default=0.7)
    parser.add_argument("-b", "--black", action="store", type=float,
                        help="Black Level value. Minimum: 0, Maximum; 255.75", default=128.0)

    args = parser.parse_args()

    with Vimba() as vimba:
        # get system object
        system = vimba.getSystem()

        # list available cameras (after enabling discovery for GigE cameras)
        if system.GeVTLIsPresent:
            system.runFeatureCommand("GeVDiscoveryAllOnce")
            time.sleep(0.2)
        cameraIds = vimba.getCameraIds()
        for cameraId in cameraIds:
            print 'Camera ID:', cameraId

        # get and open a camera
        camera0 = vimba.getCamera(cameraIds[0])
        camera0.openCamera()

        # set the value of a feature
        camera0.AcquisitionMode = 'Continuous'
        camera0.PixelFormat = "RGB8Packed"
        camera0.BalanceWhiteAuto = 'Continuous'
        camera0.EdgeFilter = "Sharpen1"
        camera0.ExposureTimeAbs = args.exposure
        camera0.Gamma = args.gamma
        camera0.BlackLevel = args.black

        # create new frames for the camera
        frame0 = camera0.getFrame()  # creates a frame

        def capture_im():

            image = capture_image(frame0)

            # Save images
            img = Image.frombuffer("RGB", (frame0.width, frame0.height), image, "raw", "RGB")
            img.save(os.path.join(args.directory, "{}{}.jpg".format(args.prefix, i)))
            time.sleep(float(args.frequency))

        frame0.announceFrame()
        camera0.startCapture()
        frame0.queueFrameCapture()
        camera0.runFeatureCommand('AcquisitionStart')

        if args.img_num < 0:
            i = 0
            while True:
                capture_im()
                i += 1
        else:
            for i in range(args.img_num):
                capture_im()

        camera0.runFeatureCommand('AcquisitionStop')
        camera0.endCapture()
        camera0.revokeAllFrames()


if __name__ == "__main__":
    main()
