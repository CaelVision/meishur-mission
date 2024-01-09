#!/usr/bin/env python3
import os
import onnxruntime
import time
import numpy as np
from PIL import Image

def preprocess_image(image_path, height, width):
    image = Image.open(image_path)
    image = image.resize((width, height), Image.LANCZOS)
    image_data = np.asarray(image).astype(np.float32)
    image_data = image_data.transpose([2, 0, 1])  # transpose to CHW

    for channel in range(image_data.shape[0]):
        mean = image_data[channel, :, :].mean()
        std_dev = image_data[channel, :, :].std()
        image_data[channel, :, :] = (image_data[channel, :, :] - mean) / std_dev

    image_data = np.expand_dims(image_data, 0)
    return image_data

print("TEST STARTED")

session = onnxruntime.InferenceSession(
    "/home/stephen/ws/meishur-mission/insulator-inspection/converted-model.onnx",
    # providers=["TensorrtExecutionProvider"],
    providers=["CPUExecutionProvider"],
    # providers=["CUDAExecutionProvider"],
)



directory_path = "/home/stephen/ws/insulator-classification/glass/train/images"
init_time = time.time()



for filename in os.listdir(directory_path):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        image_path = os.path.join(directory_path, filename)
        img = preprocess_image(image_path, 640, 640)

        output = session.run(output_names=[], input_feed={
            "images": img,
        })[0]

        for i in range(9):
            i += 4
            idx = np.argmax(output[0, i, :])
            val = output[0, i, idx]
            print(f"Image: {filename}; row: {i - 3};\tcol: {idx}; val: {val:8f}")

end_time = time.time()

total_time = end_time - init_time
print("TEST ENDED")
print(total_time)
