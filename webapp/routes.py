# webapp/routes.py

import os
import sys
import csv
from io import StringIO
from flask import Blueprint, render_template, request, send_file
from werkzeug.utils import secure_filename
from classifier_agent.classifier import classify_input_file
from shared_memory.memory import SharedMemory

# Add path for local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'pdf', 'json', 'txt'}

main = Blueprint('main', __name__)
mem = SharedMemory()

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def homepage():
    return render_template('home.html')

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/trynow', methods=['GET'])
def try_now():
    return render_template('trynow.html')

@main.route('/memory')
def view_memory():
    filter_type = request.args.get('type')
    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = 10

    logs = mem.fetch_all()

    if filter_type:
        logs = [log for log in logs if log[7].lower() == filter_type.lower()]
    if search:
        logs = [log for log in logs if search in str(log).lower()]

    total = len(logs)
    pages = (total + per_page - 1) // per_page
    logs = logs[(page - 1) * per_page: page * per_page]

    return render_template('memory_dashboard.html', logs=logs, page=page, pages=pages, filter_type=filter_type, search=search)

@main.route('/memory/export')
def export_memory():
    logs = mem.fetch_all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Source', 'Content', 'Result', 'Extracted Values', 'Timestamp', 'Thread ID', 'Type'])
    cw.writerows(logs)
    output = si.getvalue()
    return send_file(
        StringIO(output),
        mimetype='text/csv',
        as_attachment=True,
        download_name='memory_logs.csv'
    )

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request"

    file = request.files['file']

    if file.filename == '':
        return "No file selected"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Step 1: Classify
        format_type, intent = classify_input_file(file_path)

        # Step 2: Read content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        result = f"Classified as {intent}"

        # Step 3: Log to memory
        mem.log_memory(
            source=filename,
            type_=format_type,
            extracted_values=intent,
            content=content,
            result=result,
            thread_id="web"
        )

        return f"✅ File uploaded and processed: <b>{format_type}</b>, Intent: <b>{intent}</b>"

    return "Invalid file type"
