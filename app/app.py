import subprocess
import os
import redis
from flask import Flask, request
import pytesseract
from datetime import datetime
from PIL import Image, ImageDraw

app = Flask(__name__)

# TESTING
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
redis_client = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')

# ROOT ENDPOINT
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
        <form action="/maintenance" method="get">
            <input type="submit" value="Maintenance">
        </form>
       
        <p>Pytesseract version: {py_ver}</p>
        <p>Build time: {build_time}</p>
        <p>Current time: {current_time}</p>
    """

# UPLOAD ENDPOINT -> 1. + 2. SUBTASK
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return "No image", 400
        
        file = request.files['image']
        description = request.form.get('desc', 'No description')
        
        # TESTING
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

        # TESTING
        output_path = os.path.join(UPLOAD_FOLDER, "proc_" + file.filename)
        img.save(output_path)
        
        detected_text = " ".join([word.strip() for word in d['text'] if word.strip()])
        notification_message = f"Description: {description} | Text: {detected_text}"
        redis_client.publish('operator_notifications', notification_message)
        
        return f"""
            <p>Description: {description}.<p>
            <p>Image location for testing: {output_path}</p>
            <form action="/" method="get">
                <input type="submit" value="Return">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

# MAINTENANCE ENDPOINT -> 3. SUBTASK
@app.route('/maintenance', methods=['GET'])
def maintenance():
    try:
        keys = redis_client.keys('*')
        table_rows = ""
        for filename in keys:
            description = redis_client.get(filename)
            proc_filename = f"proc_{filename}"
            table_rows += f"""
                <tr>
                    <td>{filename}</td>
                    <td>{description}</td>
                    <td>{proc_filename}</td>
                </tr>
            """
            
        return f"""
            <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
                <tr style="background-color: #f2f2f2;">
                    <th>File name</th>
                    <th>Description</th>
                    <th>Output file name</th>
                </tr>
                {table_rows if table_rows else '<tr><td colspan="3">No uploads yet.</td></tr>'}
            </table>
            <br>
            <form action="/" method="get">
                <input type="submit" value="Return">
            </form>
            <form action="/maintenance/clear" method="post" style="display:inline;">
                <input type="submit" value="Clear Redis Database" style="background-color: red; color: white; padding: 5px 10px; border: none; cursor: pointer;">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

# CLEAR DB
@app.route('/maintenance/clear', methods=['POST'])
def clear_redis():
    try:
        redis_client.flushall()
        return """
            <p>Redis database successfully cleared!</p>
            <form action="/maintenance" method="get">
                <input type="submit" value="Back to Maintenance">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)