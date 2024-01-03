#!/usr/bin/env python3
import onnxruntime
import numpy as np
from PIL import Image

def preprocess_image(image_path, height, width):
    image = Image.open(image_path)
    image = image.resize((width, height), Image.LANCZOS)
    image_data = np.asarray(image).astype(np.float32)
    image_data = image_data.transpose([2, 0, 1]) # transpose to CHW

    # these magic numbers need furthur justification
    # why add these adjustments for each of the color channels?
    mean = np.array([0.079, 0.05, 0]) + 0.406
    std = np.array([0.005, 0, 0.001]) + 0.224
    # for channel in range(image_data.shape[0]):
    #     image_data[channel, :, :] = (image_data[channel, :, :] / 255 - mean[channel]) / std[channel]

    for channel in range(image_data.shape[0]):
       mean = image_data[channel,:,:].mean()
       std_dev = image_data[channel,:,:].std()
       image_data[channel,:,:] = (image_data[channel,:,:] - mean) / std_dev

    # insert a "batch dimension", where the input batch size is 1
    image_data = np.expand_dims(image_data, 0)
    return image_data

session = onnxruntime.InferenceSession(
  "converted-model.onnx",
  providers=["TensorrtExecutionProvider"],
  # providers=["CPUExecutionProvider"],
  # providers=["CUDAExecutionProvider"],
)

# the image size comes from session.get_inputs()[0].shape
img = preprocess_image("original.jpg", 640, 640)

output = session.run(output_names=[], input_feed={
    "images": img,
})[0]

for i in range(9):
  i += 4
  idx = np.argmax(output[0,i,:])
  val = output[0,i,idx]
  print(f"row: {i-3};\tcol: {idx}; val: {val:8f}")
