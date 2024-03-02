#!/usr/bin/env python3
import cv2
import time

import onnxruntime as ort


"""
HELPER FUNCS FROM PREVIOUS FILE

def preprocess_image(image, height, width):
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    image_data = np.asarray(image, dtype=np.float32).transpose([2, 0, 1])  # transpose to CHW

    mean = np.mean(image_data, axis=(1, 2), keepdims=True)
    std_dev = np.std(image_data, axis=(1, 2), keepdims=True)

    # Check if std_dev is zero and replace with a small non-zero value
    std_dev = np.where(std_dev == 0, 1e-8, std_dev)

    image_data = (image_data - mean) / std_dev

    return np.expand_dims(image_data, 0)

"""

# gstreamer_args = (
#     'udpsrc port={} ! '
#     'application/x-rtp, payload=96 ! '
#     '{}rtph264depay ! '
#     'decodebin ! videoconvert ! '
#     'appsink')

# gstreamer_args = (
#     "v4l2src device=/dev/video1 ! "
#     # "nvarguscamerasrc ! "
#     "video/jpeg,format=MJPG,framewmrk=30/1,width=1920,height=1080 ! "
#     "nvjpegdec ! "
#     "video/x-raw(memory:NVMM),format=I420"
#     "nvvidconv ! "
#     "appsink"
# )

# CSI camera args
# gstreamer_args = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"

# uncompressed
# gstreamer_args = f"v4l2src device=/dev/video0 ! video/x-raw, width=1080, height=720, format=NV12, framerate=30/1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"

# compressed
gstreamer_args= f"v4l2src device=/dev/video0 ! image/jpeg,format=MJPG,width=1280,height=720,framerate=30/1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! videoconvert ! video/x-raw,format=BGR ! appsink"

# print("[INFO] Loading Model....")
# session = ort.InferenceSession(
#     "/home/stephen/ws/meishur-mission/insulator-inspection/converted-model.onnx",
#     providers=["CUDAExecutionProvider"]
# )
# print("[INFO] Model Checked and loaded")

vid = cv2.VideoCapture(gstreamer_args, cv2.CAP_GSTREAMER)

print("uh device opened??")

while(True): 

    # Capture the video frame 
    # by frame 
    print("reading frame", time.time())
    ret, frame = vid.read() 

    # Display the resulting frame 
    cv2.imshow('frame', frame) 

    # Close window with q
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

# After the loop release the cap object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 
print("all windows destroyed")
