FROM python:3.9-slim-buster

USER root
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir flask requests pytesseract

RUN useradd -m pythonuser
WORKDIR /home/pythonuser/app
COPY app/app.py .
RUN chown -R pythonuser:pythonuser /home/pythonuser/app
USER pythonuser
EXPOSE 5000
CMD ["python3", "-u", "app.py"]