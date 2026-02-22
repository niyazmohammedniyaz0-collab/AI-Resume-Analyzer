from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
import PyPDF2
import docx

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'uploads'

job_skills = ["python", "aws", "flask", "docker", "sql", "nlp"]
