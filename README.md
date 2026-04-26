# Smart Face Recognition Attendance System

An intelligent attendance management system that uses face recognition, geofencing, and real-time video processing to automate and secure student attendance.

---

## Demo Video

Watch the complete working of the system here:  
https://drive.google.com/drive/folders/1CGF_-iluQiBCmrnnmswG3tn3_DabPPho

---

## Overview

This project is a full-stack attendance system designed to ensure accurate and secure attendance marking. It uses live video streaming to detect and recognize faces, verifies the user's location using GPS, and records attendance only when all conditions are satisfied.

The system also includes a complete admin panel for managing students, monitoring attendance, and updating records.

---

## Features

### Student Features
- Face-based attendance marking
- Login using PRN and email
- Real-time attendance capture
- Attendance percentage calculation
- Personal dashboard with attendance summary

### Admin Features
- Dashboard showing total, present, and absent students
- Manual attendance update functionality
- Student registration and management
- Individual attendance report viewing
- Dynamic class timing configuration

### Core System Capabilities
- Real-time webcam video streaming
- Face detection and recognition using stored dataset
- GPS-based geofencing to restrict attendance to classroom area
- Database-driven class time validation
- Prevention of duplicate attendance entries
- Attendance analytics

---

## Screenshots
Flowchart of the system:-
<img width="594" height="679" alt="Screenshot 2026-01-13 233451" src="https://github.com/user-attachments/assets/21744e0e-e9e5-4db9-bf65-c12f62a7e73f" />
Welcome Page:-
<img width="1883" height="915" alt="Screenshot 2026-01-19 151246" src="https://github.com/user-attachments/assets/5d5dbb69-fee1-4a6e-bed6-519e27eb6fc3" />

Attendance page:
<img width="1889" height="924" alt="Screenshot 2026-01-07 185240" src="https://github.com/user-attachments/assets/a4547a80-a5ea-4740-8b75-6d6e09d87b7f" />
Admin dashboard:-
<img width="1892" height="814" alt="Screenshot 2026-01-01 193807" src="https://github.com/user-attachments/assets/04f5c69f-31a9-40d8-955f-f5a2465410d7" />


## Tech Stack

Frontend:
- HTML
- CSS
- JavaScript
- Chart.js

Backend:
- Python (Flask)

Computer Vision:
- OpenCV
- face_recognition
- YOLO (Ultralytics)

Database:
- MySQL

---

## Project Structure


project/

 app.py
 dataset/ # Stored face images
 static/ # CSS, JS, Images
 templates/ # HTML files
 screenshots/ # Project screenshots
 requirements.txt
 README.md


---

## Requirements

All dependencies are listed in the `requirements.txt` file.

---

## Installation and Setup

### 1. Clone the repository

git clone https://github.com/your-username/face-attendance-system.git

cd face-attendance-system


### 2. Install dependencies

pip install -r requirements.txt


### 3. Setup MySQL database

Create database:

CREATE DATABASE attendance_db;


Create required tables:
- student_database  
- Student_attendance  
- class_timing  

---

### 4. Configure environment variables

Create a `.env` file and add:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=attendance_db
SECRET_KEY=your_secret_key


---

### 5. Run the application

python app.py


Open in browser:

http://localhost:5000


---

## Dataset

The system uses a local dataset of student face images stored in the `dataset/` folder.

Each image must be named using the student's PRN.

Example:

12345.jpg


---

## System Workflow

1. Student registers with personal details and face image  
2. Face image is stored in the dataset  
3. During attendance:
   - GPS location is verified  
   - Camera is activated  
   - Face is detected and matched  
4. If all conditions are satisfied:
   - Attendance is recorded in the database  

---

## Security Features

- Geofencing-based access control  
- Session-based authentication  
- Prevention of duplicate attendance  
- Class time restriction using database  

---

## Known Issues

- Face recognition accuracy may decrease in low lighting  
- Requires camera and location permissions  
- Performance may vary depending on system hardware  

---

## Limitations

- Depends on dataset quality for accuracy  
- Designed primarily for local deployment  
- Requires proper lighting for optimal performance  

---

## Future Enhancements

- Cloud deployment (AWS, Render, etc.)  
- Email notifications for attendance  
- Improved mobile responsiveness  
- Advanced face recognition models  
- Multi-classroom support  

---

## Contributing

Contributions are welcome.

1. Fork the repository  
2. Create a new branch  
3. Make changes  
4. Submit a pull request  



## Acknowledgements

This project uses open-source libraries for computer vision and machine learning and pre trained YOLOv11 model.


## Author

Harshal Patil
