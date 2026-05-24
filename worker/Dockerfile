FROM python:3.10-slim
RUN pip install redis
WORKDIR /app
COPY worker.py .
CMD ["python", "worker.py"]