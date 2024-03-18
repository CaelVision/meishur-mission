#!/usr/bin/env python3
import cv2
import time
import onnxruntime as ort
import numpy as np
import PIL as Image

DETECTION_THRESH = 0.3

def preprocess_image(img, height, width):
    image = cv2.resize(img, (width, height), interpolation=cv2.INTER_LANCZOS4)
    image_data = np.asarray(image).astype(np.float32)
    image_data = image_data.transpose([2, 0, 1])  # transpose to CHW

    for channel in range(image_data.shape[0]):
        mean = image_data[channel, :, :].mean()
        std_dev = image_data[channel, :, :].std()
        image_data[channel, :, :] = (image_data[channel, :, :] - mean) / std_dev

    image_data = np.expand_dims(image_data, 0)
    return image_data



# CSI camera args
# gstreamer_args = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"

# uncompressed
# gstreamer_args = f"v4l2src device=/dev/video0 ! video/x-raw, width=1080, height=720, format=NV12, framerate=30/1 ! nvvidconv ! video/x-raw, format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"

# compressed
gstreamer_args= f"v4l2src device=/dev/video1 ! image/jpeg,format=MJPG,width=800,height=600,framerate=30/1 ! nvv4l2decoder mjpeg=1 ! nvvidconv ! videoconvert ! video/x-raw,format=BGR ! appsink"

print("[INFO] Loading Model....")
session = ort.InferenceSession(
    "/home/stephen/ws/meishur-mission/insulator-inspection/converted-model.onnx",
    providers=["CUDAExecutionProvider"]
)

with open("class_names.txt") as f:
  class_names = f.read().splitlines()

print("[INFO] Model Checked and loaded")

vid = cv2.VideoCapture(gstreamer_args, cv2.CAP_GSTREAMER)

print("uh device opened??")

while(True): 

    # Capture the video frame 
    # by frame 
    print("reading frame", time.time())
    ret, frame = vid.read() 

    imageData = preprocess_image(frame, 640, 640)

    # Display the resulting frame 
    cv2.imshow('frame', frame)

    # Use model
    output = session.run(output_names=[], input_feed={"images": imageData})[0].squeeze()
    
    probabilities = output[4:,:]

    if np.max(probabilities) > DETECTION_THRESH:

        result = np.argsort(probabilities, axis=1)

        # take the last three columns and reverse the order to descending
        result = result[:,-3:][:,::-1]

        # print outputs
        print("\n-----")
        for i, n in enumerate(class_names):
            print(f"{n}: {probabilities[i,result[i,0]]}")
        print("-----\n")

    # Close window with q
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

# After the loop release the cap object 
vid.release() 
# Destroy all the windows 
cv2.destroyAllWindows() 
print("all windows destroyed")


