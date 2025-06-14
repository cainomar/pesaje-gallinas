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

def extraer_pesos_desde_imagen(ruta_imagen):
    imagen = cv2.imread(ruta_imagen)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, binaria = cv2.threshold(gris, 150, 255, cv2.THRESH_BINARY_INV)

    texto = pytesseract.image_to_string(binaria, config='--psm 6')
    lineas = texto.split('\n')

    pesos = []
    for linea in lineas:
        for palabra in linea.split():
            try:
                peso = float(palabra.replace(',', '.'))
                if 500 < peso < 5000:
                    pesos.append(peso)
            except:
                continue

    return pesos

def calcular_estadisticas(pesos):
    if not pesos:
        return None

    total = len(pesos)
    promedio = sum(pesos) / total
    desv_std = np.std(pesos)
    cv = (desv_std / promedio) * 100
    dentro_rango = [p for p in pesos if promedio * 0.9 <= p <= promedio * 1.1]
    uniformidad = (len(dentro_rango) / total) * 100

    return {
        'total_aves': total,
        'peso_promedio': round(promedio, 2),
        'coef_variacion': round(cv, 2),
        'uniformidad': round(uniformidad, 2)
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    if request.method == 'POST':
        archivo = request.files['imagen']
        if archivo:
            filename = secure_filename(archivo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            archivo.save(filepath)

            pesos = extraer_pesos_desde_imagen(filepath)
            resultados = calcular_estadisticas(pesos)

    return render_template('index.html', resultados=resultados)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
