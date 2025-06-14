from flask import Flask, render_template, request
import pytesseract
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_weights_from_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    text = pytesseract.image_to_string(binary, config='--psm 6')
    lines = text.split('\n')
    weights = [int(w) for w in lines if w.strip().isdigit()]
    return weights

def calculate_stats(weights):
    total = len(weights)
    avg = round(sum(weights) / total, 2) if total else 0
    std_dev = round(np.std(weights), 2)
    cv = round((std_dev / avg) * 100, 2) if avg else 0
    uniformity = round(
        sum(1 for w in weights if abs(w - avg) <= 0.1 * avg) / total * 100, 2
    ) if total else 0
    return {
        'total_aves': total,
        'peso_promedio': avg,
        'coef_variacion': cv,
        'uniformidad': uniformity
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        file = request.files['imagen']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            weights = extract_weights_from_image(filepath)
            results = calculate_stats(weights)
    return render_template('index.html', resultados=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
