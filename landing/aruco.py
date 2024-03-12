#!/usr/bin/env python3
import numpy as np
import cv2
import cv2.aruco as aruco
import math

#--- Define Tag
ARUCO_ID  = 950
MARKER_SIZE  = 20 #- [cm]

#--- Get the camera calibration path
calib_path  = "./chessboard-photos/"
camera_matrix   = np.loadtxt(calib_path+'cameraMatrix.txt', delimiter=',')
camera_distortion   = np.loadtxt(calib_path+'cameraDistortion.txt', delimiter=',')

#--- 180 deg rotation matrix around the x axis
R_flip  = np.zeros((3,3), dtype=np.float32)
R_flip[0,0] = 1.0
R_flip[1,1] =-1.0
R_flip[2,2] =-1.0

objp = np.array([
  [0, 0, 0],
  [1, 0, 0],
  [1, 1, 0],
  [0, 1, 0],
], np.float32)
objp[:,:2] -= 0.5
objp *= MARKER_SIZE

#--- Define the aruco dictionary
aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)
# parameters  = aruco.DetectorParameters_create()
parameters = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, parameters)

#--- Capture the videocamera (this may also be a video or a picture)
cap = cv2.VideoCapture(0)
#-- Set the camera size as the one it was calibrated with
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
new_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, camera_distortion, (1280,720), 1, (1280,720))
# print("new_matrix", new_matrix)

#-- Font for the text in the image
font = cv2.FONT_HERSHEY_PLAIN

while True:

    #-- Read the camera frame
    ret, frame = cap.read()
    frame = cv2.undistort(frame, camera_matrix, camera_distortion, None, new_matrix)

    #-- Convert in gray scale
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #-- remember, OpenCV stores color images in Blue, Green, Red

    #-- Find all the aruco markers in the image
    corners, ids, rejected = detector.detectMarkers(gray, None, None, None)
    
    if ids is not None and ids[0] == ARUCO_ID:
        
        # print(f"objp: {objp}")

        # print(f"corners: {corners[0]}")
        _, rvec, tvec = cv2.solvePnP(objp, corners[0], new_matrix, camera_distortion)
        print(f"height: {tvec[2]}")
        # print(f"tvec: {tvec}")

        #-- Unpack the output, get only the first
        # rvec, tvec = ret[0][0,0,:], ret[1][0,0,:]

        #-- Draw the detected marker and put a reference frame over it
        aruco.drawDetectedMarkers(frame, corners)
        # aruco.drawAxis(frame, camera_matrix, camera_distortion, rvec, tvec, 10)
        cv2.drawFrameAxes(frame, new_matrix, camera_distortion, rvec, tvec, 10)

        #-- Print the tag position in camera frame
        str_position = "MARKER Position x=%4.0f  y=%4.0f  z=%4.0f"%(tvec[0], tvec[1], tvec[2])
        cv2.putText(frame, str_position, (0, 100), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        #-- Obtain the rotation matrix tag->camera
        R_ct    = np.matrix(cv2.Rodrigues(rvec)[0])
        R_tc    = R_ct.T

        #-- Now get Position and attitude f the camera respect to the marker
        pos_camera = -R_ct*np.matrix(tvec)
        # pos_camera = -R_tc*np.matrix(tvec)

        str_position = "CAMERA Position x=%4.0f  y=%4.0f  z=%4.0f"%(pos_camera[0], pos_camera[1], pos_camera[2])
        cv2.putText(frame, str_position, (0, 200), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

    #--- Display the frame
    cv2.imshow('frame', frame)

    #--- use 'q' to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break
