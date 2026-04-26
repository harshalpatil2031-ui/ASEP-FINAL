# Smart Face Recognition Attendance System

This project is a full-stack attendance management system that automates student attendance using face recognition, geofencing, and real-time video processing. It is designed to ensure accuracy, prevent proxy attendance, and provide a complete dashboard for both students and administrators.

---

## Overview

The system captures live video, detects and recognizes faces, verifies the user's location, and marks attendance only if all conditions are satisfied. It also provides administrative controls for managing students, updating attendance, and monitoring overall statistics.

---

## Features

### Student Features
- Face-based attendance marking
- Secure login using PRN and email
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
- Basic analytics for attendance tracking

---

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
│
├── app.py
├── dataset/ # Stored face images
├── static/ # CSS, JS, Images
├── templates/ # HTML files
├── requirements.txt
└── README.md

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


Create tables:
- student_database
- Student_attendance
- class_timing

(Define schema based on your implementation)

---

### 4. Configure environment variables

Create a `.env` file:
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

## System Workflow

1. Student registers with personal details and face image  
2. Face image is stored in the dataset  
3. During attendance:
   - GPS location is verified  
   - Camera is activated  
   - Face is detected and matched  
4. If conditions are satisfied:
   - Attendance is marked in the database  

---

## Security Features

- Geofencing-based access control
- Session-based authentication
- Prevention of duplicate attendance
- Class time restriction using database

---

## Limitations

- Requires proper lighting for accurate face recognition
- Performance depends on dataset quality
- Currently optimized for local deployment

---

## Future Enhancements

- Cloud deployment support
- Email notifications for attendance updates
- Improved mobile responsiveness
- Advanced face recognition models
- Multi-classroom and multi-user scalability

---

## Contributing

Contributions are welcome.

1. Fork the repository  
2. Create a new branch  
3. Make your changes  
4. Submit a pull request  

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


## Demo Video

Watch the complete working of the system here:
https://drive.google.com/drive/folders/1CGF_-iluQiBCmrnnmswG3tn3_DabPPho

## Author

Harshal Patil
