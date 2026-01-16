from symtable import Class
import cv2
from datetime import datetime
from ultralytics import YOLO
import face_recognition, os, mysql.connector
import time as t  
from datetime import date
from flask import Flask, render_template, Response, request,render_template_string, session , redirect, url_for 
import re
import math


# ------------------------ Globals ------------------------------
streaming = False
camera = None
model=YOLO('yolo11n.pt')

known_face_encode = []
known_face_prn = []
known_face_name = []
logged_prns = set()
#---------------- Geofence Settings ------------------------
CLASSROOM_LAT = 18.46784
CLASSROOM_LON = 73.85778
ALLOWED_RADIUS_METERS = 300

# ---------- CLASS TIME ----------
CLASS_START = 8
CLASS_END = 24
#-------------DISTANCE CALCULATION FUNCTION -------------------------
def is_inside_classroom(lat, lon):
    R = 6371000  # Earth radius in meters

    lat1 = math.radians(CLASSROOM_LAT)
    lon1 = math.radians(CLASSROOM_LON)
    lat2 = math.radians(lat)
    lon2 = math.radians(lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c

    return distance <= ALLOWED_RADIUS_METERS
# ------------------------ Load Known Faces ------------------------
def load_known_faces(directory="dataset"):
    for filename in os.listdir(directory):
        if filename.endswith((".jpg", ".png")):
            image = face_recognition.load_image_file(os.path.join(directory, filename))
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encode.append(encodings[0])
                prn = os.path.splitext(filename)[0]
                known_face_prn.append(prn)
                known_face_name.append(prn)
#------------------------ Class Time Check ------------------------

def is_class_time():
    now_hour = datetime.now().hour
    return CLASS_START <= now_hour <= CLASS_END
# ------------------------ Mark Attendance ------------------------

def mark_attendance(prn, name):
    if not is_class_time():
        return

    if prn in logged_prns:
        return

    logged_prns.add(prn)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Student_attendance (prn, name, attendance_date, time, status)
        VALUES (%s, %s, CURDATE(), CURTIME(), 'Present')
        ON DUPLICATE KEY UPDATE
            status='Present',
            time=CURTIME()
    """, (prn, name))

    conn.commit()
    cursor.close()
    conn.close()

#------------------------ Check Already Marked ------------------------
def already_marked_today(name):
    conn = mysql.connector.connect(
        host="localhost", user="root",
        password="Cristiano@107", database="attendance_db"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM Student_attendance
        WHERE name=%s AND attendance_date=CURDATE()
    """, (name,))
    exists = cursor.fetchone()
    cursor.close()
    conn.close()
    return exists is not None
#------------------------ Dashboard Stats ------------------------
def get_dashboard_stats():
    """
    Returns total students, present today, absent today
    """
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(DISTINCT name) AS total,
            SUM(status='Present') AS present,
            SUM(status='Absent') AS absent
        FROM Student_attendance
        WHERE attendance_date = CURDATE()
    """)
    total, present, absent = cursor.fetchone()

    cursor.close()
    conn.close()

    return total or 0, present or 0, absent or 0



# ------------------------ Video Stream ------------------------
def generate_frames():
    global camera, streaming

    while streaming:
        if camera is None:
            t.sleep(0.1)
            continue

        success, frame = camera.read()
        if not success:
            continue

        results = model(frame, conf=0.5, verbose=False)

        if not is_class_time():
            cv2.putText(
                frame,
                "Outside Class Time",
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 0, 255),
                3
            )
        else:
            for result in results:
                if not streaming:
                    break

                for box in result.boxes:
                    if not streaming:
                        break

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    face_img = frame[y1:y2, x1:x2]

                    if face_img.size == 0:
                        continue

                    rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                    encodings = face_recognition.face_encodings(rgb_face)

                    if encodings:
                        matches = face_recognition.compare_faces(
                            known_face_encode,
                            encodings[0]
                        )
                        if True in matches:
                            idx = matches.index(True)
                            prn = known_face_prn[idx]
                            name = known_face_name[idx]

                            mark_attendance(prn, name)


                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                            cv2.putText(
                                frame,
                                "Attendance Marked: " + name,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (255, 0, 0),
                                2
                            )
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(
                            frame,
                            "Unknown",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 0, 255),
                            2
                        )

        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )
#---------------------------- Class Time Check -----------------------
def is_class_time():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cur = conn.cursor()
    cur.execute("SELECT start_time, end_time FROM class_timing ORDER BY id DESC LIMIT 1")
    start_time, end_time = cur.fetchone()
    cur.close()
    conn.close()

    now = datetime.now().time()
    return start_time <= now <= end_time


# ------------------------ Flask App ------------------------
app = Flask(__name__, template_folder=r"C:\Users\Harshal\OneDrive\Desktop\Face recognition System")
app.secret_key="Harshal"

# ------------------------ Routes ------------------------
@app.route("/")
def home():
    return render_template("Website.html",page="home")

@app.route("/studentManagement", methods=["POST"])
def studentmanagement():
    name = request.form["name"]
    roll_no = request.form["roll_no"]
    prn = request.form["prn"]
    branch = request.form["branch"]
    email = request.form["email"]

    conn = mysql.connector.connect(
        host="localhost", user="root", password="Cristiano@107", database="attendance_db"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO student_database (name, roll_no, prn, branch, email)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, roll_no, prn, branch, email))
    conn.commit()
    cursor.execute("SELECT * FROM student_database")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("Student.html", message=f"Student {name} registered successfully!", students=students)

UPLOAD_FOLDER = "dataset"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )
def clean_name(name):
   
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    
    name = name.strip().replace(" ", "_")
    return name
@app.route("/register", methods=["POST"])
def register():
    
    name = request.form["name"]
    roll_no = request.form["roll_no"]
    prn = request.form["prn"]
    branch = request.form["branch"]
    email = request.form["email"]
    file = request.files["file"]

    
    if not all([name, roll_no, prn, branch, email, file]):
        return "Missing data"

    if not allowed_file(file.filename):
        return "Invalid file type"



    # Connect to database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO student_database (name, roll_no, prn, branch, email)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, roll_no, prn, branch, email))
    conn.commit()
    cursor.close()
    conn.close()

    
    filename = prn + ".jpg"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    return render_template("Success.html", message=f" Student {name} registered successfully!")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        prn = request.form["prn"]
        email = request.form["email"]
        action = request.form.get("action")

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Cristiano@107",
            database="attendance_db"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM student_database WHERE prn=%s AND email=%s",
            (prn, email)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return render_template(
                "Website.html",
                page="login",
                error="Incorrect PRN or Email"
            )

        
        session["prn"] = user["prn"]
        session["name"] = user["name"]

        if action == "dashboard":
            return redirect(url_for("student_dashboard"))

        if action == "attendance":
            return render_template("Website.html", page="attendance")

    return render_template("Website.html", page="login")


    
    return render_template("Website.html", page="login")



@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/start_camera")
def start_camera_route():
    global camera, streaming

    if not session.get("gps_allowed"):
        return "Unauthorized", 403

    if not streaming:
        camera = cv2.VideoCapture(0)
        t.sleep(0.5)  # 🔥 VERY IMPORTANT
        streaming = True

    return "", 204


@app.route("/stop_camera")
def stop_camera():
    global camera, streaming
    streaming = False
    if camera:
        camera.release()
        camera = None
    session.pop("gps_allowed", None) 
    return "", 204


@app.route("/attendance/<name>")
def attendance(name):
    safe_name = name.strip().replace(" ", "_")
    filename = os.path.join("static", f"{safe_name}.csv")

    if not os.path.exists(filename):
        return f"<h3>No attendance file found for {name}</h3>"

    # Read CSV and build HTML table
    import csv
    rows = []
    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # Simple HTML table
    table_html = "<table border='1'>"
    for row in rows:
        table_html += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
    table_html += "</table>"
    table_html += "<br><button onclick=\"window.location.href='/'\">Back to Home</button>"

    return render_template_string(table_html)


@app.route("/set_location", methods=["POST"])
def set_location():
    lat = float(request.form.get("latitude"))
    lon = float(request.form.get("longitude"))

    print("GPS RECEIVED:", lat, lon)

    inside = is_inside_classroom(lat, lon)
    print("INSIDE CLASSROOM:", inside)

    if not inside:
        return "", 403   # 👈 important

    session["gps_allowed"] = True
    return "", 204
    
   
@app.route("/attendance_page")
def attendance_page():
    return render_template("Website.html", page="attendance")


@app.route("/student_dashboard")
def student_dashboard():
    if "prn" not in session:
        return redirect(url_for("login"))

    prn = session["prn"]

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_days,
            SUM(status='Present') AS present_days
        FROM Student_attendance
        WHERE prn=%s
    """, (prn,))

    total_days, present_days = cursor.fetchone()
    cursor.close()
    conn.close()

    total_days = total_days or 0
    present_days = present_days or 0
    percentage = round((present_days / total_days) * 100, 2) if total_days else 0

    return render_template(
        "Website.html",
        page="dashboard",
        attendance=present_days,
        total=total_days,
        percentage=percentage,
        student_name=session.get("name"),
        student_prn=prn
    )

@app.route("/admin_dashboard")
def admin_dashboard():
    total, present, absent = get_dashboard_stats()

    return render_template(
        "Website.html",
        page="admin_dashboard",
        total_students=total,
        present_today=present,
        absent_today=absent
    )
@app.route("/admin_update_attendance", methods=["POST"])
def admin_update_attendance():
    prn = request.form["prn"]
    status = request.form["status"]

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Student_attendance
        SET status=%s, time=CURTIME()
        WHERE prn=%s AND attendance_date=CURDATE()
    """, (status, prn))

    # Insert if not exists
    if cursor.rowcount == 0:
        cursor.execute("""
            INSERT INTO Student_attendance (prn,name, attendance_date, time, status)
            VALUES (%s, %s, CURDATE(), CURTIME(), %s)
        """, (prn, status))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))
@app.route("/admin_show_attendance", methods=["POST"])
def admin_show_attendance():
    prn = request.form.get("prn")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cur = conn.cursor()

    # ---------- Student attendance ----------
    cur.execute("SELECT COUNT(*) FROM Student_attendance WHERE prn=%s", (prn,))
    total = cur.fetchone()[0] or 0

    cur.execute(
        "SELECT COUNT(*) FROM Student_attendance WHERE prn=%s AND status='Present'",
        (prn,)
    )
    present = cur.fetchone()[0] or 0

    absent = total - present
    percentage = round((present / total) * 100, 2) if total > 0 else 0

    # ---------- Dashboard stats ----------
    cur.execute("""
        SELECT
            COUNT(DISTINCT name),
            SUM(status='Present'),
            SUM(status='Absent')
        FROM Student_attendance
        WHERE attendance_date = CURDATE()
    """)
    total_students, present_today, absent_today = cur.fetchone()

    cur.close()
    conn.close()

    attendance_data = {
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": percentage
    }

    return render_template(
        "Website.html",
        page="admin_dashboard",
        attendance_data=attendance_data,
        total_students=total_students or 0,
        present_today=present_today or 0,
        absent_today=absent_today or 0
    )
#------------------------ Set Class Time ------------------------
@app.route("/set_class_time", methods=["POST"])
def set_class_time():
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Cristiano@107",
        database="attendance_db"
    )
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO class_timing (start_time, end_time) VALUES (%s, %s)",
        (start_time, end_time)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ------------------------ Main ------------------------
if __name__ == "__main__":
    load_known_faces()
    app.run(host="0.0.0.0", port=5000, debug=True,use_reloader= False )