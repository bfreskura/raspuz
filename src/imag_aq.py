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
        cameras = []
        images = dict()
        for cameraId in cameraIds:
            print 'Camera ID:', cameraId
            save_dir = os.path.join(args.directory, cameraId)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # get and open a camera
            camera = vimba.getCamera(cameraId)
            camera.openCamera()

            # set the value of a feature
            camera.AcquisitionMode = 'Continuous'
            camera.PixelFormat = "RGB8Packed"
            camera.BalanceWhiteAuto = 'Continuous'
            camera.EdgeFilter = "Sharpen1"
            camera.ExposureTimeAbs = args.exposure
            camera.Gamma = args.gamma
            camera.BlackLevel = args.black

            # create new frames for the camera
            frame = camera.getFrame()  # creates a frame

            frame.announceFrame()
            camera.startCapture()
            frame.queueFrameCapture()
            camera.runFeatureCommand('AcquisitionStart')

            cameras.append((camera, frame, cameraId, save_dir))
            images[cameraId] = []

        def capture_im(frame):
            time.sleep(float(args.frequency))

            return capture_image(frame)

        if args.img_num < 0:
            i = 0
            print "Press CTRL + C to stop image acquisition"
            while True:
                try:
                    for c, f, id, d in cameras:
                        images[id].append(capture_im(f))
                    i += 1
                except KeyboardInterrupt:
                    break
        else:
            for i in range(args.img_num):
                for c, f, id, d in cameras:
                    images[id].append(capture_im(f))

        for c, f, id, d in cameras:
            c.runFeatureCommand('AcquisitionStop')
            c.endCapture()
            c.flushCaptureQueue()
            c.revokeAllFrames()
            save_to_disk(images[id], f, channels=3, dir=d, prefix=args.prefix)


if __name__ == "__main__":
    main()
