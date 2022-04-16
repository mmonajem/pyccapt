import time
import cv2

import numpy as np

#from pypylon import pylon
from tools import variables


class Camera:
    """
        This camera modules is designed to setup and intiate the camera in the installation.
        This camera module allows user to capture images using the installed cameras,
        process the image and display as per desired window size.

    """

    def __init__(self, devices, tlFactory, cameras, converter):
        """
        Constructor function which intializes and setups all variables
        and parameter for the class.
        """
        self.devices = devices
        self.tlFactory = tlFactory
        self.cameras = cameras
        self.converter = converter
        self.cameras[0].Open()
        self.cameras[0].ExposureAuto.SetValue('Off')
        self.cameras[0].ExposureTime.SetValue(1000000)
        self.cameras[1].Open()
        self.cameras[1].ExposureAuto.SetValue('Off')
        self.cameras[1].ExposureTime.SetValue(350000)

    def update_cameras(self, lock):

        """
        Note : Changed function to break it down into simpler functions

        This class method setup the cameras to capture the required images. It initiates
        image capture for all cameras attached starting with index 0.The grabbing
        set up for free-running continuous acquisition.

        Attributes:
            lock: object to acquire and release locks.
        Returns:
            Does not return anything.

        """
        self.cameras.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        while self.cameras.IsGrabbing():

            # Fetch the raw images from camera
            grabResult0 = self.cameras[0].RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            grabResult1 = self.cameras[1].RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

            image0 = self.converter.Convert(grabResult0)
            img0 = image0.GetArray()
            image1 = self.converter.Convert(grabResult1)
            img1 = image1.GetArray()

            # Original size is 2048 * 2448
            # Resize the original to the required size. Utlize the openCV tool.
            img0_orig = cv2.resize(img0, dsize=(2048, 2048), interpolation=cv2.INTER_CUBIC).astype(np.int32)
            img0_zoom = cv2.resize(img0[800:1100, 1800:2300], dsize=(1200, 500), interpolation=cv2.INTER_CUBIC).astype(
                np.int32)

            img1_orig = cv2.resize(img1, dsize=(2048, 2048), interpolation=cv2.INTER_CUBIC).astype(np.int32)
            img1_zoom = cv2.resize(img1[1120:1300, 1000:1520], dsize=(1200, 500), interpolation=cv2.INTER_CUBIC).astype(
                np.int32)

            # Store the captured processed image at a desired location.
            if variables.index_save_image % 100 == 0 and variables.start_flag:
                cv2.imwrite(variables.path + "/side_%s.png" % variables.index_save_image, img0_orig)
                cv2.imwrite(variables.path + "/side_zoom_%s.png" % variables.index_save_image, img0_zoom)
                cv2.imwrite(variables.path + '/bottom_%s.png' % variables.index_save_image, img1_orig)
                cv2.imwrite(variables.path + '/bottom_zoom_%s.png' % variables.index_save_image, img1_zoom)

            # The function cv::drawMarker draws a marker on a given position in the image. 
            img0_zoom_marker = cv2.drawMarker(img0_zoom, (1050, 310), (0, 0, 255), markerType=cv2.MARKER_TRIANGLE_UP,
                                              markerSize=40, thickness=2, line_type=cv2.LINE_AA)
            img1_zoom_marker = cv2.drawMarker(img1_zoom, (1100, 285), (0, 0, 255), markerType=cv2.MARKER_TRIANGLE_UP,
                                              markerSize=40, thickness=2, line_type=cv2.LINE_AA)

            # Acquire the lock and releases after process using context manager
            # To ensure that the marked array is a C-contiguous array
            with lock:
                variables.img0_zoom = np.require(img0_zoom_marker, np.uint8, 'C')
                variables.img1_zoom = np.require(img1_zoom_marker, np.uint8, 'C')

                # Interchange two axes of an array.
                variables.img0_orig = np.swapaxes(img0_orig, 0, 1)
                variables.img1_orig = np.swapaxes(img1_orig, 0, 1)
                variables.index_save_image += 1

            # Store the captured processed image at a desired location.
            if variables.index_save_image % 100 == 0 and variables.start_flag:
                cv2.imwrite(variables.path + "/side_%s.png" % variables.index_save_image, img0_orig)
                cv2.imwrite(variables.path + "/side_zoom_%s.png" % variables.index_save_image, img0_zoom)
                cv2.imwrite(variables.path + '/bottom_%s.png' % variables.index_save_image, img1_orig)
                cv2.imwrite(variables.path + '/bottom_zoom_%s.png' % variables.index_save_image, img1_zoom)

            grabResult0.Release()
            grabResult1.Release()

            if variables.sample_adjust:
                self.camera_s_d()
                variables.sample_adjust = False

    def light_switch(self, ):
        """
            This class methid sets the Exposure time based on a flag.
            It reads the flag from the imported "vairables" file.

            Attributes:
                Does not accept any arguments.
            Return:
                Does not return anything.
        """
        if not variables.light:
            self.cameras[0].Open()
            self.cameras[0].ExposureTime.SetValue(2000)
            self.cameras[1].Open()
            self.cameras[1].ExposureTime.SetValue(2000)
            variables.light = True
            variables.sample_adjust = True
        elif variables.light:
            self.cameras[0].Open()
            self.cameras[0].ExposureTime.SetValue(1000000)
            self.cameras[1].Open()
            self.cameras[1].ExposureTime.SetValue(350000)
            variables.light = False
            variables.sample_adjust = False

    def camera_s_d(self, ):
        """
        This class method captures the images through the cameras, processes it
        and displays the processed image. Utilizes OpenCv module and Numpy modules
        to process the captured image. Utlizes OpenCV module to display the captured
        image in a window.

        Attributes:
            Does not accept any arguments
        Return
            Does not return anything.
        """

        # The exit code of the sample application.
        img0 = []
        img1 = []
        windowName = 'Sample Alignment'

        # Initiates a while loop which checks if the camera is grabbing the images.
        while self.cameras.IsGrabbing():
            if not self.cameras.IsGrabbing():
                break

            try:
                grabResult = self.cameras.RetrieveResult(200, pylon.TimeoutHandling_ThrowException)

                # When the cameras in the array are created the camera context value
                # is set to the index of the camera in the array.
                # The camera context is a user settable value.
                # This value is attached to each grab result and can be used
                # to determine the camera that produced the grab result.
                cameraContextValue = grabResult.GetCameraContext()

                if grabResult.GrabSucceeded():
                    image = self.converter.Convert(grabResult)  # Access the openCV image data

                    if cameraContextValue == 0:  # If camera 0, save array into img0[]
                        img0 = image.GetArray()
                    else:  # if camera 1, save array into img1[]
                        img1 = image.GetArray()

                    # If there is no img1, the first time, make img1=img0
                    # Need the same length arrays to concatenate
                    if len(img1) == 0:
                        img1 = img0

                    img0_zoom = cv2.resize(img0[800:1100, 1800:2300], dsize=(2448, 1000), interpolation=cv2.INTER_CUBIC)
                    img1_zoom = cv2.resize(img1[1100:1350, 1000:1550], dsize=(2448, 1000),
                                           interpolation=cv2.INTER_CUBIC)
                    img0_zoom = cv2.drawMarker(img0_zoom, (2150, 620), (0, 0, 255),
                                               markerType=cv2.MARKER_TRIANGLE_UP,
                                               markerSize=80, thickness=2, line_type=cv2.LINE_AA)
                    img1_zoom = cv2.drawMarker(img1_zoom, (2100, 530), (0, 0, 255),
                                               markerType=cv2.MARKER_TRIANGLE_UP,
                                               markerSize=80, thickness=2, line_type=cv2.LINE_AA)
                    img0_f = np.concatenate((img0, img0_zoom), axis=0)
                    img1_f = np.concatenate((img1, img1_zoom), axis=0)
                    vis = np.concatenate((img0_f, img1_f), axis=1)  # Combine 2 images horizontally
                    # Label the window
                    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
                    # Resize the window
                    cv2.resizeWindow(windowName, 2500, 1200)
                    # displays image in specified window
                    cv2.imshow(windowName, vis)
                    k = cv2.waitKey(1)
                    # Close all windows when ESC key is pressed.
                    if k == 27:  # If press ESC key
                        print('ESC')
                        cv2.destroyAllWindows()
                        break
            except:
                pass

            grabResult.Release()
            time.sleep(0.05)

            # If window has been closed using the X button, close program
            # getWindowProperty() returns -1 as soon as the window is closed
            if cv2.getWindowProperty(windowName, 0) < 0 or not variables.light_swich:
                grabResult.Release()
                cv2.destroyAllWindows()
                break
