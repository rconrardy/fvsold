visions = {
    "mainfoveal": {
        "ratio": 1/3,
        "size": 100,
        "jobs": ["log"]
    },
    "parafoveal": {
        "ratio": 2/3,
        "size": 100,
        "jobs": ["curr", "detection"]
    },
    "peripheral": {
        "ratio": 3/3,
        "size": 100,
        "jobs": ["gray"]
    }
}
detection = {
    "classes": ["background", "aeroplane", "bicycle", "bird", "boat",
	    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	    "sofa", "train", "tvmonitor"],
    "prototxt": "C:\\Users\\conra\\Documents\\detection\\MobileNetSSD_deploy.prototxt.txt",
    "model": "C:\\Users\\conra\\Documents\\detection\\MobileNetSSD_deploy.caffemodel",
    "confidence": 0.7
}
gimbal = {
    "attached": False
}
