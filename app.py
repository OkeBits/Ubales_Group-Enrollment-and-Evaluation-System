from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import os
import random
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'users.db'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                email TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                fullname TEXT,
                lrn TEXT,
                birthdate TEXT,
                age INTEGER,
                placeofbirth TEXT,
                phone TEXT,
                email TEXT,
                mothername TEXT,
                motheroccupation TEXT,
                fathername TEXT,
                fatheroccupation TEXT,
                year INTEGER,
                course TEXT,
                enroll_type TEXT,
                image_filename TEXT,
                subject TEXT,
                instructor TEXT,
                room TEXT
            )
        ''')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        db = get_db()
        g.user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


course_subjects = {
  "BSIT 1": {
    "Monday": [ ("", "NO CLASS", "") ],
    "Tuesday": [ ("07:00 – 10:00", "DISCREET MATHEMATICS", "Ms. NINAL", "Room 1A"), ("10:00 – 01:00", "GRAPHICS DESIGN", "MR. CASOCOT", "Room 2A") ],
    "Wednesday": [ ("07:00 – 10:00", "PURPOSIVE COMMUNICATION", "MR. PASCUAL", "Room 2B"), ("10:00 – 01:00", "LIFE AND WORKS OF RIZAL", "MS. MUSTAPHA", "Room 2C") ],
    "Thursday": [ ("07:00 – 10:00", "PROGRAMMING 2", "MR. MANIWANG", "Room 3A"), ("10:00 – 01:00", "FUNDAMENTALS OF DATABASE SYSTEM", "MR. CASOCOT", "Room 3B") ],
    "Friday": [ ("07:00 – 10:00", "WEBSITE DESIGN", "MR. CASOCOT", "Room 3C"), ("10:00 – 01:00", "WEB DEVELOPMENT", "MR. MANIWANG", "Room 3D") ],
    "Saturday": [ ("07:00 – 09:00", "PATHFIT 2", "MR. LACIDA", "Gym 1"), ("10:00 – 01:00", "CWTS 2", "MR. LACIDA", "Gym 2") ],
    "Sunday": [ ("", "NO CLASS", "") ]
  },
  "BSIT 2": {
    "Monday": [ ("", "NO CLASS", "") ],
    "Tuesday": [ ("", "NO CLASS", "") ],
    "Wednesday": [ ("", "NO CLASS", "") ],
    "Thursday": [ ("", "NO CLASS", "") ],
    "Friday": [ ("", "NO CLASS", "") ],
    "Saturday": [ ("02:00 – 04:00", "SPORTS", "MR. MORAL", "Gym 1"), ("04:00 – 07:00", "OBJECT-ORIENTED PROGRAMMING", "MS. LINCOPINIS", "Room 2A") ],
    "Sunday": [ ("07:00 – 10:00", "WEB SYSTEM AND TECHNOLOGY", "MS. LINCOPINIS", "Room 2B"), ("10:00 – 01:00", "GUI-BASED APPLICATION", "MR. RANDY CANETE", "Room 2C"), ("01:00 – 04:00", "ART APPRECIATION", "MR. SAPUTALO", "Room 3A"), ("04:00 – 07:00", "INTERNSHIP", "MR.LINAO", "Room 3B") ]
  },
  "BSIT 3": {
    "Monday": [ ("07:00 – 10:00", "NETWORKING", "MR. MANIWANG", "Room 3C"), ("10:00 – 01:00", "INFORMATION ASSURANCE & SECURITY 2", "MR. CASOCOT", "Room 3D") ],
    "Tuesday": [ ("", "NO CLASS", "") ],
    "Wednesday": [ ("", "NO CLASS", "") ],
    "Thursday": [ ("", "NO CLASS", "") ],
    "Friday": [ ("", "NO CLASS", "") ],
    "Saturday": [ ("07:00 – 10:00", "METHODS OF RESEARCH IN COMPUTING", "MS. CALANDA", "Room 1A"), ("10:00 – 01:00", "INTEGRATIVE PROGRAMMING TECHNOLOGY", "MR. GOMEZ", "Room 2A"), ("01:00 – 04:00", "CAPSTONE PROJECT 1 & RESEARCH 1", "MR. WATAMAMA", "Room 2B"), ("04:00 – 07:00", "ETHICS", "MR. LABATIGAN", "Room 2C") ],
    "Sunday": [ ("07:00 – 10:00", "CONTEMPORARY WORLD", "MR. SAPUTALO", "Room 3A"), ("10:00 – 01:00", "HUMAN COMPUTER INTERACTION", "MR. RAMBOY", "Room 3B") ]
  },
  "BSIT 4": {
    "Monday": [ ("", "NO CLASS", "") ],
    "Tuesday": [ ("", "NO CLASS", "") ],
    "Wednesday": [ ("", "NO CLASS", "") ],
    "Thursday": [ ("", "NO CLASS", "") ],
    "Friday": [ ("", "NO CLASS", "") ],
    "Saturday": [ ("", "NO CLASS", "") ],
    "Sunday": [ ("07:00 – 10:00", "GENDER & SOCIETY", "MR. SITOY", "Room 3C"), ("10:00 – 04:00", "OJT", "MR. SEBIAL", "Room 3D") ]
  },

  "BTVTED 1": {
    "Monday": [
      ("07:00 – 10:00", "HUMAN COMPUTER INTERACTION", "MR. GOMEZ", "Room 1A"),
      ("10:00 – 01:00", "CWTS", "MR. DEGUIT", "Room 2A")
    ],
    "Tuesday": [
      ("07:00 – 10:00", "THE CHILD ADOLESCENT", "DR. RAPADAS", "Room 3A"),
      ("10:00 – 01:00", "PATHFIT 2", "MR. WAPER", "Room 2B")
    ],
    "Wednesday": [
      ("07:00 – 10:00", "ETHICS", "MS. MUSTAPHA", "Room 3B"),
      ("10:00 – 01:00", "CONTEMPORARY WORLD", "MR. ESIO", "Room 2C")
    ],
    "Thursday": [("","NO CLASS","")],
    "Friday": [("","NO CLASS","")],
    "Saturday": [
      ("07:00 – 10:00", "ART APPRECIATION", "MS. LABATIGAN", "Room 3C"),
      ("10:00 – 01:00", "PHILLIPINE INDIGENOUS", "MR. ABACAHIN", "Room 3D"),
      ("01:00 – 04:00", "GENDER & SOCIETY", "MR. LABATIGAN", "Room 1A"),
      ("04:00 – 07:00", "THE TEACHING PROFFESSION", "MS. CABANG", "Room 2A")
    ],
    "Sunday": [("","NO CLASS","")]
  },
  "BTVTED 2": {
    "Monday": [
      ("07:00 – 10:00", "HE LITERACY", "MS. CANETE", "Room 2B"),
      ("10:00 – 01:00", "COMPUTER PROGRAMMING 2", "MR. GOMEZ", "Room 3A")
    ],
    "Tuesday": [
      ("07:00 – 10:00", "INTRO TO AFA", "MR. MORAL", "Room 3B"),
      ("10:00 – 01:00", "TEACHING ICT AS AN EXPLORATORY COURSE", "MR. GOMEZ", "Room 2C")
    ],
    "Wednesday": [("","NO CLASS","")],
    "Thursday": [
      ("07:00 – 10:00", "SPORTS", "MR. MORAL", "Gym 2"),
      ("10:00 – 01:00", "FOUNDATION OF SPED", "DR. RAPADAS", "Room 3D")
    ],
    "Friday": [("","NO CLASS","")],
    "Saturday": [
      ("07:00 – 10:00", "CURRICULUM DEVELOPMENT WITH EMPHASIS ON TM II", "MS. BIADNES", "Room 1A"),
      ("10:00 – 01:00", "ASSESSMENT OF LEARNING 2", "MR. ELLUNODO", "Room 2A"),
      ("01:00 – 04:00", "PROF ED – 10", "MR. MADELO", "Room 3A"),
      ("04:00 – 07:00", "TTL 2", "MS. JUNARD LLAGAS", "Room 2B")
    ],
    "Sunday": [
      ("04:00 – 07:00", "GMAW", "MR. POLOYAPOY", "Room 3C")
    ]
  },
  "BTVTED 3": {
    "Monday": [
      ("07:00 – 10:00", "DATABASE MANAGEMENT", "MS. CABARDO", "Room 3D"),
      ("10:00 – 01:00", "COMPUTER SYSTEM AND DATA", "MR. MANIWANG", "Room 1A")
    ],
    "Tuesday": [("","NO CLASS","")],
    "Wednesday": [("","NO CLASS","")],
    "Thursday": [
      ("07:00 – 10:00", "NETWORK, ADMIN & MAINTENANCE", "MR. CABARDO", "Room 2A"),
      ("10:00 – 01:00", "LIVING IN THE IT ERA", "MR. MANIWANG", "Room 3B")
    ],
    "Friday": [("","NO CLASS","")],
    "Saturday": [
      ("07:00 – 10:00", "COMMON COMPETENCIES IN AFA", "MR. J. LLAGAS", "Room 2C"),
      ("10:00 – 01:00", "COMMON COMPETENCIES IN HE", "MR. J. LLAGAS", "Room 3C"),
      ("01:00 – 04:00", "TR 2", "DR. BINCAL", "Room 1A"),
      ("04:00 – 07:00", "CAPSTONE", "MS. CALAMBA", "Room 2B")
    ],
    "Sunday": [
      ("04:00 – 07:00", "WORK-BASED LEARNING WITH EMPHASIS ON TM", "MR. MADEL", "Room 3D")
    ]
  },
  "BTVTED 4": {
    "Monday": [
      ("07:00 – 10:00", "DATABASE MANAGEMENT", "MS. CABARDO", "Room 1A"),
      ("10:00 – 01:00", "COMPUTER SYSTEM AND DATA", "MR. MANIWANG", "Room 2A")
    ],
    "Tuesday": [("","NO CLASS","")],
    "Wednesday": [("","NO CLASS","")],
    "Thursday": [("","NO CLASS","")],
    "Friday": [("","NO CLASS","")],
    "Saturday": [("","NO CLASS","")],
    "Sunday": [
      ("07:00 – 01:00", "PRACTICE TEACHING", "DR. RAPADAS", "Room 2B"),
      ("01:00 – 07:00", "IN-HOUSE REVIEW", "MR. J. ILLAGAS", "Room 3A")
    ]
  },

"BAELS 1": {
    "Monday": [("","NO CLASS","")],
    "Tuesday": [
        ("07:00 – 10:00", "INTRO. TO ENGLISH LANGUAGE SYSTEM", "MR. MORAL", "Room 1A"),
        ("10:00 – 01:00", "UNDERSTANDING THE SELF", "DR. RAPADAS", "Room 2A")
    ],
    "Wednesday": [
        ("07:00 – 10:00", "ETHICS", "DR. RAPADAS", "Room 2B"),
        ("10:00 – 01:00", "CWTS", "MS. AGANOS", "Room 2C")
    ],
    "Thursday": [
        ("10:00 – 01:00", "CWTS", "MS. AGANOS", "Room 3A")
    ],
    "Friday": [("","NO CLASS","")],
    "Saturday": [
        ("07:00 – 10:00", "THEORIES OF LANGUAGE ACQUISITION", "MR. CASIBUAL", "Room 3B"),
        ("10:00 – 01:00", "PATHFIT 2", "MR. ALCASID", "Room 3C"),
        ("01:00 – 04:00", "CONTEMPORARY WORLD", "MR. DENNIS", "Room 3D")
    ],
    "Sunday": [("","NO CLASS","")]
},
"BAELS 2": {
    "Monday": [
        ("5:30 – 8:30", "SEMANTICS OF ENGLISH", "MS. PASCUAL", "Room 1A")
    ],
    "Tuesday": [
        ("5:30 – 8:30", "INTRO TO LANGUAGE & SOCIETY CULTURE", "MS. PASCUAL", "Room 2A")
    ],
    "Wednesday": [
        ("5:30 – 8:30", "INTRODUCTION TO PRAGMATICS", "MS. PASCUAL", "Room 2B")
    ],
    "Thursday": [
        ("5:30 – 8:30", "SCIENCE, TECHNOLOGY & SOCIETY", "MS. ORTEGA", "Room 2C")
    ],
    "Friday": [
        ("5:30 – 8:30", "JAPANESE 2", "MR. ABARQUEZ", "Room 3A")
    ],
    "Saturday": [
        ("07:00 – 09:00", "SPORTS", "MR. MORAL", "Room 3B"),
        ("01:00 – 04:00", "LANGUAGE OF LITERARY TEXT", "MR. CRUZ", "Room 3C")
    ],
    "Sunday": [("","NO CLASS","")]
},
"BAELS 3": {
    "Monday": [
        ("5:30 – 8:30", "LANGUAGE RESEARCH", "MS. PACILAN", "Room 3D")
    ],
    "Tuesday": [
        ("5:30 – 8:30", "PHILLIPINE POPULAR CULTURE", "MS. BIADNES", "Room 1A")
    ],
    "Wednesday": [
        ("5:30 – 8:30", "ELT APPROACHES & METHODS", "MS. SACAPANO", "Room 2A")
    ],
    "Thursday": [
        ("5:30 – 8:30", "INSTRUCTIONAL MATERIALS DEVELOPMENT", "MS. CRUZ", "Room 2B")
    ],
    "Friday": [
        ("5:30 – 8:30", "LANGUAGE & GENDER", "MR. SACAPANO", "Room 2C")
    ],
    "Saturday": [
        ("01:00 – 04:00", "ARABIC 1", "MR. GULOY", "Room 3A")
    ],
    "Sunday": [("","NO CLASS","")]
},
"BAELS 4": {
    "Monday": [
        ("5:30 – 8:30", "TECHNICAL WRITING IN THE PROFESSION", "MS. PACILAN", "Room 3B")
    ],
    "Tuesday": [
        ("5:30 – 8:30", "BUSINESS COMMUNICATION", "MS. BIADNES", "Room 3C")
    ],
    "Wednesday": [
        ("5:30 – 8:30", "ENVIRONMENTAL SCIENCE", "MS. SACAPANO", "Room 3D")
    ],
    "Thursday": [
        ("5:30 – 8:30", "PHILLIPINE INDIGENOUS COMMUNICATION", "MS. CRUZ", "Room 1A")
    ],
    "Friday": [
        ("5:30 – 8:30", "LIFE WORKS OF RIZAL", "MR. SACAPANO", "Room 2A")
    ],
    "Saturday": [("","NO CLASS","")],
    "Sunday": [("","NO CLASS","")]
},

"ACT 1": {
    "Monday": [
        ("07:00 – 10:00", "INTRO TO COMPUTING", "MR. GARCIA", "Room 1A"),
        ("10:00 – 01:00", "BASIC PROGRAMMING", "MR. REYES", "Room 2A")
    ],
    "Tuesday": [
        ("07:00 – 10:00", "DIGITAL LITERACY", "MS. SANTOS", "Room 2B"),
        ("10:00 – 01:00", "MATHEMATICS FOR COMPUTING", "MR. LOPEZ", "Room 2C")
    ],
    "Wednesday": [
        ("07:00 – 10:00", "WEB DESIGN & DEVELOPMENT", "MS. FERRER", "Room 3A"),
        ("10:00 – 01:00", "DATABASE SYSTEMS", "MR. ALONSO", "Room 3B")
    ],
    "Thursday": [
        ("07:00 – 10:00", "BASIC NETWORKING", "MS. MANALO", "Room 3C"),
        ("10:00 – 01:00", "HUMANITIES & SOCIAL SCIENCES", "MS. ZULUETA", "Room 3D")
    ],
    "Friday": [
        ("07:00 – 10:00", "TECHNOLOGY IN EDUCATION", "MS. CORDOVA", "Room 1A"),
        ("10:00 – 01:00", "COMPUTER HARDWARE TECHNICIAN", "MR. VALENZUELA", "Room 2A")
    ],
    "Saturday": [
        ("07:00 – 10:00", "SPORTS", "MR. MENDOZA", "Room 2B"),
        ("10:00 – 01:00", "PATHFIT 1", "MS. DIAZ", "Room 2C")
    ],
    "Sunday": [("","NO CLASS","")]
},
"ACT 2": {
    "Monday": [
        ("07:00 – 10:00", "ADVANCED PROGRAMMING", "MS. RAMOS", "Room 3A"),
        ("10:00 – 01:00", "COMPUTER NETWORKING", "MR. BERMUDEZ", "Room 3B")
    ],
    "Tuesday": [
        ("07:00 – 10:00", "DATABASE ADMINISTRATION", "MR. CASTRO", "Room 3C"),
        ("10:00 – 01:00", "SYSTEMS ANALYSIS & DESIGN", "MS. MENDOZA", "Room 3D")
    ],
    "Wednesday": [
        ("07:00 – 10:00", "OBJECT-ORIENTED PROGRAMMING", "MR. SANTIAGO", "Room 1A"),
        ("10:00 – 01:00", "SOFTWARE ENGINEERING", "MR. GARCIA", "Room 2A")
    ],
    "Thursday": [
        ("07:00 – 10:00", "WEB DEVELOPMENT", "MR. FERNANDEZ", "Room 2B"),
        ("10:00 – 01:00", "ELECTIVE: MOBILE APP DEVELOPMENT", "MS. FERRER", "Room 2C")
    ],
    "Friday": [
        ("07:00 – 10:00", "NETWORK SECURITY", "MS. SANTOS", "Room 3A"),
        ("10:00 – 01:00", "SOFTWARE TESTING & QUALITY ASSURANCE", "MR. VILLANUEVA", "Room 3B")
    ],
    "Saturday": [
        ("07:00 – 10:00", "INTERNSHIP PREPARATION", "MS. RIVERA", "Room 3C"),
        ("10:00 – 01:00", "RESEARCH IN IT", "MR. JAVIER", "Room 3D")
    ],
    "Sunday": [("","NO CLASS","")]
}
}
def assign_subjects_and_instructors(course, year, day_of_week=None):
    subjects_for_day = course_subjects.get(course, {}).get(day_of_week, [])
    if subjects_for_day:
        return subjects_for_day
    return [("No Class", "")]

def get_schedule(course, year):
    schedule = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        schedule[day] = assign_subjects_and_instructors(course, year, day)
    return schedule

@app.route('/student_schedule/<course>/<year>')
def student_schedule(course, year):
    schedule = get_schedule(course, year)
    return render_template('schedule.html', schedule=schedule)

def generate_student_id():
    return random.randint(100000, 999999)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        db = get_db()
        try:
            db.execute('INSERT INTO users (fullname, email, username, password) VALUES (?, ?, ?, ?)',
                       (fullname, email, username, password_hash))
            db.commit()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Username already exists!", 409
    return render_template('register.html')

@app.route('/enroll')
def enroll():
    if g.user:
        return render_template('enroll.html', user=g.user)
    return redirect(url_for('index'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/submit_enrollment', methods=['POST'])
def submit_enrollment():
    data = request.form
    fullname = data['fullname']
    lrn = data['lrn']
    birthdate = data['date']
    age = data['age']
    placeofbirth = data['placeofbirth']
    phone = data['phone']
    email = data['email']
    mothername = data['mothername']
    motheroccupation = data['motheroccupation']
    fathername = data['fathername']
    fatheroccupation = data['fatheroccupation']
    year = data['year']
    course = data['course']
    enroll_type = data['type']

    image_filename = None
    if 'profile_image' in request.files:
        image = request.files['profile_image']
        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    subject, instructor = assign_subjects_and_instructors(course, year)[0]

    # Define a list of rooms (you can customize this list as needed)
    rooms = ["1A", "2A", "2B", "2C", "3A", "3B", "3C", "3D", "Gym 1", "Gym 2"]
    room = random.choice(rooms)  # Select a random room from the list

    student_id = generate_student_id()

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO enrollments (
            student_id, fullname, lrn, birthdate, age, placeofbirth, phone,
            email, mothername, motheroccupation, fathername, fatheroccupation,
            year, course, enroll_type, image_filename, subject, instructor, room
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, fullname, lrn, birthdate, age, placeofbirth, phone,
        email, mothername, motheroccupation, fathername, fatheroccupation,
        year, course, enroll_type, image_filename, subject, instructor, room
    ))
    conn.commit()
    conn.close()

    return redirect(url_for('student_profile', student_id=student_id))

@app.route('/enrolled')
def enrolled():
    q = request.args.get('q', '')
    db = get_db()
    if q:
        enrollments = db.execute(
            "SELECT * FROM enrollments WHERE fullname LIKE ?",
            (f"%{q}%",)
        ).fetchall()
    else:
        enrollments = db.execute('SELECT * FROM enrollments').fetchall()
    return render_template('enrolled.html', enrollments=enrollments)

@app.route('/student_profile/<int:student_id>')
def student_profile(student_id):
    db = get_db()
    enrollment = db.execute('SELECT * FROM enrollments WHERE student_id = ?', (student_id,)).fetchone()
    if enrollment:
        course = enrollment['course']
        year = str(enrollment['year'])
        schedule = get_schedule(f"{course} {year}", year)
        return render_template('schedule.html', enrollment=enrollment, schedule=schedule)
    return redirect(url_for('enrolled'))

@app.route('/delete_enrollment/<int:student_id>', methods=['POST'])
def delete_enrollment(student_id):
    db = get_db()
    db.execute('DELETE FROM enrollments WHERE student_id = ?', (student_id,))
    db.commit()
    return redirect(url_for('enrolled'))

@app.route('/dashboard')
def dashboard():
    if g.user:
        return render_template('dashboard.html', user=g.user)
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    return "Invalid username or password", 401

@app.route('/recover', methods=['POST'])
def recover():
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

