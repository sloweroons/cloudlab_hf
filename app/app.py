import subprocess
import os
import redis
from flask import Flask, request
import pytesseract
from PIL import Image, ImageDraw

app = Flask(__name__)

# Könyvtár a képeknek
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Redis kapcsolat
redis_client = redis.Redis(host='my-redis-master', port=6379, decode_responses=True)

@app.route("/")
def root():
    return "<h1>Szerver fut!</h1><p>Próbáld ki a /test vagy /upload végpontokat.</p>"

@app.route("/test")
def test_ocr():
    try:
        py_ver = pytesseract.get_tesseract_version()
        sys_ver = subprocess.check_output(["tesseract", "--version"]).decode("utf-8")
        return f"<h1>OCR Status: OK</h1><p>Pytesseract version: {py_ver}</p><pre>{sys_ver}</pre>"
    except Exception as e:
        return f"<h1>OCR Error</h1><p>{str(e)}</p>"

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return "Nincs kép a kérésben", 400
        
        file = request.files['image']
        description = request.form.get('desc', 'Nincs leírás')
        
        # Mentés és Redis regisztráció
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        redis_client.set(file.filename, description)

        # OCR és bekeretezés
        img = Image.open(filepath).convert("RGB")
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        draw = ImageDraw.Draw(img)
        for i in range(len(d['text'])):
            if d['text'][i].strip() and int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

        output_path = os.path.join(UPLOAD_FOLDER, "proc_" + file.filename)
        img.save(output_path)
        
        return f"Siker! Leírás: {description}. Feldolgozott kép mentve ide: {output_path}"
    except Exception as e:
        return f"Hiba: {str(e)}", 500

# EZ LEGYEN A FÁJL LEGUTOLSÓ KÉT SORA!
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)