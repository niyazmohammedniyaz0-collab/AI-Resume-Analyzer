# ==============================
# 📄 app.py (Complete Working Version)
# ==============================

from flask import Flask, render_template, request, redirect, session, url_for
import os
import mysql.connector

db = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PASSWORD"),
    database=os.environ.get("MYSQL_DATABASE")
)

cursor = db.cursor()

# Required job skills
job_skills = ["python", "aws", "flask", "docker", "sql", "nlp"]

# ==============================
# DATABASE SETUP
# ==============================

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ==============================
# FILE PROCESSING FUNCTIONS
# ==============================

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text.lower()


def extract_skills(text):
    found_skills = []
    for skill in job_skills:
        if skill in text:
            found_skills.append(skill)
    return found_skills

# ==============================
# AUTH ROUTES
# ==============================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except:
            return "Username already exists"
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "Invalid Credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ==============================
# MAIN APPLICATION
# ==============================

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    match_score = 0
    missing_skills = []
    found_skills = []

    if request.method == 'POST':
        file = request.files['resume']
        if file:
            if not os.path.exists('uploads'):
                os.makedirs('uploads')

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file.filename.endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                return "Unsupported file format"

            found_skills = extract_skills(text)
            match_score = int((len(found_skills) / len(job_skills)) * 100)
            missing_skills = list(set(job_skills) - set(found_skills))

    return render_template('index.html',
                           username=session['user'],
                           match_score=match_score,
                           found_skills=found_skills,
                           missing_skills=missing_skills)


if __name__ == '__main__':
    app.run(debug=True)
