import subprocess
import pytesseract
from flask import Flask

app = Flask(__name__)

@app.route("/test-ocr")
def test_ocr():
    try:
        py_ver = pytesseract.get_tesseract_version()
        sys_ver = subprocess.check_output(["tesseract", "--version"]).decode("utf-8")
        
        return f"<h1>OCR Status: OK</h1><p>Pytesseract version: {py_ver}</p><pre>{sys_ver}</pre>"
    except Exception as e:
        return f"<h1>OCR Error</h1><p>Pytesseract missing{str(e)}</p>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)