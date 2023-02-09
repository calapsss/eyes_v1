#!/usr/bin/python3
import cv2
from datetime import datetime
from time import sleep
import os
import yaml
import datetime as dt
import boto3
from picamera2 import Picamera2




#configure boto3
s3 = boto3.resource('s3')


# testing
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

# aws access props
aws_access_key_id = cfg['s3']['aws_access_key_id']
aws_secret_access_key = cfg['s3']['aws_secret_access_key']
region = cfg['s3']['region']

# photo props
image_width = cfg['image_settings']['horizontal_res']
image_height = cfg['image_settings']['vertical_res']
file_extension = cfg['image_settings']['file_extension']
file_name = cfg['image_settings']['file_name']
photo_interval = cfg['image_settings']['photo_interval'] # Interval between photo (in seconds)
image_folder = cfg['image_settings']['folder_name']

# camera info props
camera_name = cfg['camera_info']['camera_name']
camera_location = cfg['camera_info']['location_name']
camera_type = cfg['camera_info']['camera_type']


# s3 props
bucket = cfg['s3']['bucket_name']
s3_folder = cfg['s3']['folder_name']


# Set up AWS credentials
os.environ['aws_access_key_id'] = aws_access_key_id
os.environ['aws_secret_access_key'] = aws_secret_access_key
os.environ['default.region'] = region


# Grab images as numpy arrays and leave everything else to OpenCV.
face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cv2.startWindowThread()

# Camera Setup
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (image_width, image_height)}))
picam2.start()


def main():
    count = 0
    while True:
        im = picam2.capture_array()
        grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_detector.detectMultiScale(grey, 1.3, 5)
        
        
        if len(faces) != 0:
            count += 1
            out_path = f"faces/face_{count}.{file_extension}"
            #timestamp
            CURRENT_DATE = dt.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
            CURRENT_TIME = dt.datetime.now().strftime('%m%d%Y%H%M%S')
            cv2.imwrite(out_path, im)
            # Upload to S3
            s3.meta.client.upload_file(out_path, bucket, out_path,
                ExtraArgs={'Metadata': {'Capture_Type': 'face', 
                'Date': CURRENT_DATE , 
                'Time': CURRENT_TIME, 
                'Camera_Location': camera_location, 
                'Camera_Name': camera_name, 
                'Camera_Type': camera_type}}
            )
            # Delete local file
            os.remove(out_path)

            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0))

        cv2.imshow("Camera", im)

main()

    




      


