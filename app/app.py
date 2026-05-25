import subprocess
import os
import redis
from flask import Flask, request
import pytesseract
from datetime import datetime
from PIL import Image, ImageDraw

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# redis_client = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password=None)

@app.route("/")
def root():
    
    py_ver = pytesseract.get_tesseract_version()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="image">
            <input type="text" name="desc" placeholder="...">
            <input type="submit" value="Upload">
        </form>
       
        <p>Pytesseract version: {py_ver}</p>
        <p>Build time: {build_time}</p>
        <p>Current time: {current_time}</p>
    """

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return "No image", 400
        
        file = request.files['image']
        description = request.form.get('desc', 'No description')
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        redis_client.set(file.filename, description)

        img = Image.open(filepath).convert("RGB")
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        draw = ImageDraw.Draw(img)
        for i in range(len(d['text'])):
            if d['text'][i].strip() and int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

        output_path = os.path.join(UPLOAD_FOLDER, "proc_" + file.filename)
        img.save(output_path)
        
        detected_text = " ".join([word.strip() for word in d['text'] if word.strip()])

        notification_message = f"Leiras: {description} | Szoveg: {detected_text}"
        redis_client.publish('operator_notifications', notification_message)
        
        return f"Description: {description}. Image location: {output_path}"
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)