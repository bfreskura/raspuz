from pymba import *
import time
import numpy as np
from PIL import Image
import argparse
import os

def capture_image(camera, frame, channels = 3):
    """
    Captures one frame and converts it to a numpy array
    :param camera: Camera Object
    :param frame: Frame object
    :param channels: Color Depth
    :return: Image data in a numpy array of shape (height, width, channels)
    """
    frame.announceFrame()
    camera.startCapture()
    frame.queueFrameCapture()
    camera.runFeatureCommand('AcquisitionStart')
    camera.runFeatureCommand('AcquisitionStop')
    frame.waitFrameCapture()

    # clean up after capture
    camera.endCapture()
    camera.revokeAllFrames()

    return np.ndarray(buffer = frame.getBufferByteData(),
                                   dtype = np.uint8,
                                   shape = (frame.height,
                                            frame.width,
                                            channels))
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--frequency", action="store", default = 5,
                        help = "Capture frequency")
    parser.add_argument("-d", "--directory", action="store",
                        help = "Save Directory")
    parser.add_argument("-n", "--img_num", action="store",
                        help = "Number of images to capture. Negative value will capture until the user quits the program",
                        type = int, default = 1)
    parser.add_argument("-p", "--prefix", action="store",
                        help = "Image filenames prefix", default = "img_")
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
        camera0.AcquisitionMode = "SingleFrame"
        camera0.PixelFormat = "RGB8Packed"

        # create new frames for the camera
        frame0 = camera0.getFrame()    # creates a frame

        def capture():
            image = capture_image(camera0, frame0)

            # Save images
            img = Image.frombuffer("RGB", (frame0.width, frame0.height), image, "raw", "RGB")
            img.save(os.path.join(args.directory, "{}{}.jpg".format(args.prefix, i)))
            time.sleep(float(args.frequency))

        if args.img_num < 0:
            i = 0
            while True:
                capture()
                i+=1
        else:
            for i in range(args.img_num):
                capture()

if __name__ == "__main__":
    main()
