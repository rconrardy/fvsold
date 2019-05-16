import threading
import config
import math
import cv2

class FoveatedVisionSystem:
    def __init__(self, *indices):
        """
        Initialize a FoveatedVisionSystem object using camera indices.
        Parameters: *args (int): Camera Indices
        """
        self.signals = {"open": False}
        self.indices = indices
        self.devices = {i:CaptureDevice(i, self.signals) for i in self.indices}

    def open(self):
        """
        Starts a new thread to capture video frame each device.
        Parameters: none
        """
        self.signals["open"] = True
        self.threads = [threading.Thread(target=d.capture) for d in self.devices.values()]
        [thread.start() for thread in self.threads]

    def close(self):
        """
        Closes the thread capturing video from each device.
        Parameters: none
        """
        self.signals["open"] = False
        [thread.join() for thread in self.threads]

class CaptureDevice():
    def __init__(self, index, signals):
        """
        Starts a new thread to capture video frame each device.
        Parameter: index (int): camera index, signals (dict): controls for device
        """
        self.signals = signals
        self.index = index
        self.device = cv2.VideoCapture(index)
        self.visions = {"mainfoveal": None, "parafoveal": None, "peripheral": None}

    def capture(self):
        """
        Captures video frames while the CaptureDevice is open. Crops and resizes
        the frame for each vision in the visions dict.
        Parameter: none
        """
        while self.signals["open"]:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame = self.__read()
            [self.__getVision(key, frame) for key in self.visions.keys()]
            [self.__showVision(key) for key in self.visions.keys()]

    def __read(self):
        """
        Gets the frame from the device using the OpenCV library and crops the
        original frame into a square.
        Parameter: none
        """
        ret, frame = self.device.read()
        height, width, depth = frame.shape
        diff = (width - height) // 2
        return frame[:,diff:(width-diff)]

    def __getVision(self, key, frame):
        """
        Uses the key and original frame to create a new cropped and resized matrix
        for the vision specified by the key (mainfoveal, parafoveal, peripheral).
        Parameter: key (str): vision name, frame (2dlist): RGB matrix for frame
        """
        ratio = config.visions[key]["ratio"]
        new_size = (config.visions[key]["size"], config.visions[key]["size"])
        old_size = frame.shape[0]
        diff = (old_size - math.floor(old_size*ratio)) // 2
        frame = frame[diff:(old_size-diff),diff:(old_size-diff)]
        self.visions[key] = cv2.resize(frame, new_size)

    def __showVision(self, key):
        """
        Displays the specified vision as a new window.
        Parameter: key (str): vision name
        """
        cv2.namedWindow(key + str(self.index), cv2.WINDOW_NORMAL)
        cv2.resizeWindow(key + str(self.index), 600,600)
        cv2.imshow(key + str(self.index), self.visions[key])

# class Vision():
#     def __init__(self, key):
#         self.ratio = config.visions["ratio"]
#         self.size = (config.visions["size"], config.visions["size"])
#
#     def getFrame(self, old_frame):
#         old_size = old_frame.shape[0]
#         diff = (self.size[0] - math.floor(self.size[0]*self.ratio)) // 2
