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
        self.devices = {index:CaptureDevice(index, self.signals) for index in self.indices}

    def open(self):
        """
        Starts a new thread to capture video frame each device.
        Parameters: none
        """
        self.signals["open"] = True
        self.threads = [threading.Thread(target=device.capture) for device in self.devices.values()]
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
        self.visions = {key:None for key in config.visions.keys()}

    def capture(self):
        """
        Captures video frames while the CaptureDevice is open. Crops and resizes
        the frame for each vision in the visions dict.
        Parameter: none
        """
        self.visions ={key:Vision(key, self.index) for key in config.visions.keys()}
        frame = self.__read()
        [vision.getBase(frame) for vision in self.visions.values()]
        while self.signals["open"]:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame = self.__read()
            [vision.getFrame(frame) for vision in self.visions.values()]
            [vision.showVision() for vision in self.visions.values()]

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


class Vision():
    def __init__(self, key, index):
        """
        Initialize a Vision object using a key and camera index.
        Parameters: key (int/str): name of vision, index (int) camera index
        """
        self.key = key
        self.index = index
        self.ratio = config.visions[key]["ratio"]
        self.size = (config.visions[key]["size"], config.visions[key]["size"])
        self.frame = {"prev": None, "curr": None}
        self.jobs = config.visions[key]["jobs"]

    def getBase(self, old_frame):
        """
        Gets the cropped and resized current frame.
        Parameters: old_frame (Mat) the original frame
        """
        old_size = old_frame.shape[0]
        diff = (old_size - math.floor(old_size*self.ratio)) // 2
        frame = old_frame[diff:(old_size-diff),diff:(old_size-diff)]
        self.frame["curr"] = cv2.resize(frame, self.size)

    def getFrame(self, old_frame):
        """
        Gets all the different frames (including job frames).
        Parameters: old_frame (Mat) the original frame
        """
        self.frame["prev"] = self.frame["curr"]
        self.getBase(old_frame)
        [getattr(self, "get" + job)() for job in self.jobs]

    def showVision(self):
        """
        Displays the specified vision jobs as a new window.
        Parameter: None
        """
        for job in self.jobs:
            window_name = str(self.key) + job.lower() + str(self.index)
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 600,600)
            cv2.imshow(window_name, self.frame[job.lower()])

    def getDiff(self):
        """
        Gets the difference between the previous and current frame
        Parameter: None
        """
        prev_gray = cv2.cvtColor(self.frame["prev"], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(self.frame["curr"], cv2.COLOR_BGR2GRAY)
        abs_diff = cv2.absdiff(prev_gray, curr_gray)
        self.frame["diff"] = cv2.threshold(abs_diff, 30, 255, cv2.THRESH_BINARY)[1]
