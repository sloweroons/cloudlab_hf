import subprocess
import os
import redis
from flask import Flask, request
import pytesseract
from datetime import datetime
from PIL import Image, ImageDraw
import boto3
import time
from botocore.exceptions import EndpointConnectionError

app = Flask(__name__)

# TESTING
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
redis_client = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')

s3_client = boto3.client(
    's3',
    endpoint_url='http://manual-minio-service:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='adminpass'
)
BUCKET_NAME = 'ocr-images'
while True:
    try:
        s3_client.list_buckets()
        break
    except (EndpointConnectionError, Exception):
        time.sleep(2)

try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception:
    pass

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
        <form action="/database" method="get">
            <input type="submit" value="Database">
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

        img = Image.open(filepath).convert("RGB")
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        draw = ImageDraw.Draw(img)
        for i in range(len(d['text'])):
            if d['text'][i].strip() and int(d['conf'][i]) > 60:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                draw.rectangle([x, y, x + w, y + h], outline="red", width=3)

        # TESTING
        _filename = "_" + file.filename
        output_path = os.path.join(UPLOAD_FOLDER, _filename)
        img.save(output_path)
        
        detected_text = " ".join([word.strip() for word in d['text'] if word.strip()])
        description_and_text = f"{description};{detected_text}"
        redis_client.set(file.filename, description_and_text)
        redis_client.publish('operator_notifications', description_and_text)

        s3_client.upload_file(Filename=output_path, Bucket=BUCKET_NAME, Key=f"proc_{file.filename}")
        external_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': f"proc_{file.filename}"},
            ExpiresIn=3600
        ).replace('http://manual-minio-service:9000', 'http://localhost:30009')
        
        return f"""
            <p>Description: {description_and_text}.<p>
            <p>Image location for testing: {output_path}</p>
            <form action="/" method="get">
                <input type="submit" value="Back to Home">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

# DB ENDPOINT -> 3. SUBTASK
@app.route('/database', methods=['GET'])
def database():
    try:
        keys = redis_client.keys('*')
        table_rows = ""
        for filename in keys:
            description_and_text = redis_client.get(filename)

            try:
                raw_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': f"proc_{filename}"},
                    ExpiresIn=3600
                )
                external_url = raw_url.replace('http://manual-minio-service:9000', 'http://localhost:30009')
                image = f'<img src="{external_url}" alt="Processed Image" style="max-width: 150px; height: auto;">'            except Exception:

            table_rows += f"""
                <tr>
                    <td>{filename}</td>
                    <td>{description_and_text}</td>
                    <td>{image}</td>
                </tr>
            """
            
        return f"""
            <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
                <tr style="background-color: #f2f2f2;">
                    <th>File name</th>
                    <th>Description</th>
                    <th>Processed Image</th>
                </tr>
                {table_rows if table_rows else '<tr><td colspan="3">No uploads yet.</td></tr>'}
            </table>
            <br>
            <form action="/" method="get">
                <input type="submit" value="Back to Home">
            </form>
            <form action="/database/clear" method="post" style="display:inline;">
                <input type="submit" value="Clear Redis Database" style="background-color: red; color: white; padding: 5px 10px; border: none; cursor: pointer;">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

# CLEAR DB
@app.route('/database/clear', methods=['POST'])
def clear_redis():
    try:
        redis_client.flushall()
        return """
            <p>Redis database flushed</p>
            <form action="/" method="get">
                <input type="submit" value="Back to Home">
            </form>
            <form action="/database" method="get">
                <input type="submit" value="Back to Database">
            </form>
        """
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)