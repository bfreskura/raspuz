import argparse
import os
import time
import signal
import sys

import numpy as np
from PIL import Image
from pymba import *



def capture_image(frame, channels=3, frame_wait=1000):
    """
    Captures one frame and converts it to a numpy array
    :param frame_wait: Time in miliseconds to give camera in order to process acquired image
    :param frame: Frame object
    :param channels: Color Depth
    :return: Image data in a numpy array of shape (height, width, channels)
    """
    frame.waitFrameCapture(timeout=frame_wait)
    img = frame.getBufferByteData()
    data = convert_to_np_array(img, frame, channels)
    frame.queueFrameCapture()

    return np.copy(data)


def convert_to_np_array(img, frame, channels):
    return np.ndarray(buffer=img,
                      dtype=np.uint8,
                      shape=(frame.width,
                             frame.height,
                             channels))


def save_to_disk(imgs, frame, channels, dir, prefix):
    # Save images
    print("Saving images. This could take a while...")
    for i, img in enumerate(imgs):
        img = Image.frombuffer("RGB", (frame.width, frame.height), img, "raw", "RGB")
        img.save(os.path.join(dir, "{}{}.jpg".format(prefix, i)))

    print("Saving finished")

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
                        help="Exposure Time. Minimum: 26, Maximum: 60000000", default=200000.0)
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

        # Temporary Images array
        images = []

        def capture_im():
            time.sleep(float(args.frequency))

            return capture_image(frame0)

        frame0.announceFrame()
        camera0.startCapture()
        frame0.queueFrameCapture()
        camera0.runFeatureCommand('AcquisitionStart')

        if args.img_num < 0:
            i = 0
            print "Press CTRL + C to stop image acquisition"
            while True:
                try:
                    images.append(capture_im())
                    i += 1
                except KeyboardInterrupt:
                    break

        else:
            for i in range(args.img_num):
                images.append(capture_im())

        camera0.runFeatureCommand('AcquisitionStop')
        camera0.endCapture()
        camera0.flushCaptureQueue()
        camera0.revokeAllFrames()

        save_to_disk(images, frame0, channels=3, dir=args.directory, prefix=args.prefix)


if __name__ == "__main__":
    main()
