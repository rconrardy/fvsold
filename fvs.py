import numpy as np
import threading
import serial
import copy
import config
import math
import cv2

class FoveatedVisionSystem:
    def __init__(self, *indices):
        """
        Initialize a FoveatedVisionSystem object using camera indices.
        Parameters: *args (int): Camera Indices
        """
        self.signals = {"open": False, "gimbal": config.gimbal["attached"]}
        self.devices = [CaptureDevice(index, self.signals) for index in indices]
        if self.signals["gimbal"]:
            self.gimbals = [GimbalMount(self.signals)]

    def open(self):
        """
        Starts a new thread to capture video frame each device.
        Parameters: none
        """
        self.signals["open"] = True
        self.device_threads = [threading.Thread(target=device.capture) for device in self.devices]
        [thread.start() for thread in self.device_threads]
        if self.signals["gimbal"]:
            self.gimbal_threads = [threading.Thread(target=gimbal.listen) for gimbal in self.gimbals]
            [thread.start() for thread in self.gimbal_threads]

    def close(self):
        """
        Closes the thread capturing video from each device.
        Parameters: none
        """
        self.signals["open"] = False
        [device.cap.release for device in self.devices]
        [thread.join() for thread in self.device_threads]
        [thread.join() for thread in self.gimbal_threads]

class CaptureDevice():
    def __init__(self, index, signals):
        """
        Starts a new thread to capture video frame each device.
        Parameter: index (int): camera index, signals (dict): controls for device
        """
        self.signals = signals
        self.index = index
        self.cap = cv2.VideoCapture(index)
        self.visions = {key:None for key in config.visions.keys()}

    def capture(self):
        """
        Captures video frames while the CaptureDevice is open. Crops and resizes
        the frame for each vision in the visions dict.
        Parameter: none
        """
        self.visions ={key:Vision(key, self.index) for key in config.visions.keys()}
        frame = self.__read()
        # [vision.getBase(frame) for vision in self.visions.values()]
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
        ret, frame = self.cap.read()
        height, width, channels = frame.shape
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
        if "detection" in self.jobs:
            prototxt = config.detection["prototxt"]
            model = config.detection["model"]
            self.net = cv2. cv2.dnn.readNetFromCaffe(prototxt, model)
            self.confidence = config.detection["confidence"]
            self.classes = config.detection["classes"]
            self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
            print(self.net)

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
        [getattr(self, "get" + job.lower().capitalize())() for job in self.jobs if job not in ["curr", "prev"]]

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

    def getGray(self):
        """
        Gets the gray version of the current frame
        Parameter: None
        """
        self.frame["gray"] = cv2.cvtColor(self.frame["curr"], cv2.COLOR_BGR2GRAY)

    def getEdge(self):
        """
        Gets the edges of the current frame
        Parameter: None
        """
        self.frame["edge"] = cv2.Canny(self.frame["curr"], 100, 200)

    def getDiff(self):
        """
        Gets the difference between the previous and current frame
        Parameter: None
        """
        prev_gray = cv2.cvtColor(self.frame["prev"], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(self.frame["curr"], cv2.COLOR_BGR2GRAY)
        abs_diff = cv2.absdiff(prev_gray, curr_gray)
        self.frame["diff"] = cv2.threshold(abs_diff, 30, 255, cv2.THRESH_BINARY)[1]

    def getLog(self):
        """
        Gets the log polar of the current frame
        Parameter: None
        """
        new_size = (self.frame["curr"].shape[0]/2, self.frame["curr"].shape[1]/2)
        self.frame["log"] = cv2.logPolar(self.frame["curr"], new_size, 40, cv2.WARP_FILL_OUTLIERS)

    def getLinear(self):
        """
        Gets the linear polar of the current frame
        Parameter: None
        """
        new_size = (self.frame["curr"].shape[0]/2, self.frame["curr"].shape[1]/2,)
        self.frame["linear"] = cv2.linearPolar(self.frame["curr"], new_size, 40, cv2.WARP_FILL_OUTLIERS)

    def getDetection(self):
        """
        Gets the recognized object within the frame
        Parameter: None
        """
        blob = cv2.dnn.blobFromImage(cv2.resize(self.frame["curr"], (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        self.frame["detection"] = copy.deepcopy(self.frame["curr"])
        (h, w) = self.frame["detection"].shape[:2]
        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.confidence:
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                label = "{}: {:.2f}%".format(self.classes[idx], confidence * 100)
                cv2.rectangle(self.frame["detection"], (startX, startY), (endX, endY), self.colors[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(self.frame["detection"], label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[idx], 2)


    def getTrack(self):
        """
        Tracks an object in the current frame
        Parameter: None
        """
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.calcBackProject([hsv], [0], )


class GimbalMount():
    def __init__(self, signals):
        """
        Initialize a GimbalMount object using the signals.
        Parameters: signals (dict): controls for device
        """
        self.signals = signals
        self.ser = serial.Serial('COM4', baudrate = 9600, timeout = 1)

    def listen(self):
        """
        Listen for signals to the gimbal for movement
        Parameter: None
        """
        while(self.signals["open"]):
            userInput = input('Enter input: ')
            self.ser.write(str.encode(userInput))
            arduinoData = self.ser.readline().decode('ascii')
            print(arduinoData)
            arduinoData = self.ser.readline().decode('ascii')
            print(arduinoData)
