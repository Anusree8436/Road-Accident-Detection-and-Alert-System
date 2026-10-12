Road Accident Detection and Alert System

Project Overview

A Python-based Road Accident Detection and Alert System using YOLOv8 and OpenCV. The system analyzes traffic video footage to detect vehicles, track their movements, and identify potential road accidents. When a possible accident is detected, it automatically sends an email alert with approximate location information and a Google Maps link.

Technologies Used

Python – Main programming language

YOLOv8 – Vehicle detection

OpenCV – Video processing and visualization

ByteTrack – Vehicle tracking across frames

NumPy – Numerical calculations

IoU (Intersection over Union) – Bounding-box overlap analysis

SMTP (Gmail) – Email alert notifications

IPinfo API – Approximate IP-based location retrieval

Google Maps – Location link generation

How It Works

OpenCV reads the input traffic video frame by frame.

YOLOv8 detects vehicles such as cars, motorcycles, buses, and trucks.

ByteTrack assigns tracking IDs to follow vehicles across consecutive frames.

The system calculates bounding-box overlap using IoU and monitors vehicle movement.

If overlapping vehicles remain stationary for a specified number of frames, the system flags a potential accident.

An automatic email alert is sent with approximate location information and a Google Maps link.

Key Features

Vehicle detection using YOLOv8

Multi-object tracking using ByteTrack

IoU-based vehicle overlap analysis

Stationary-vehicle monitoring across multiple frames

Automatic email notifications

Approximate location information with Google Maps link

Installation and Setup

1. Clone the repository

git clone https://github.com/Anusree8436/Road-Accident-Detection-and-Alert-System.git
cd Road-Accident-Detection-and-Alert-System

2. Install required libraries

pip install ultralytics opencv-python numpy requests

3. Add an input video

Place a traffic video in the project folder and update the video filename in main.py if necessary.

4. Configure email settings

Set the following environment variables:

ALERT_EMAIL – Sender Gmail address

ALERT_EMAIL_PASSWORD – Sender's Google App Password

RECEIVER_EMAIL – Receiver email address

Do not store your actual email password in the source code.

5. Run the project

python main.py

Project Structure

Road-Accident-Detection-and-Alert-System/
├── main.py
├── alert_system.py
├── .gitignore
└── README.md

The YOLOv8 model weights and input videos are excluded from the repository. The pretrained yolov8n.pt weights can be downloaded automatically by Ultralytics when required.

Limitations and Future Improvements

Heavy traffic and stationary vehicles may sometimes trigger false alerts.

Accident-detection performance requires further evaluation using labeled video footage.

IP-based location is approximate and does not necessarily represent the accident location.

Future improvements include better collision analysis, reducing false alerts, and more accurate location integration.

Author

Anusree K

Computer Science and Engineering Graduate

Interested in Artificial Intelligence, Machine Learnin
