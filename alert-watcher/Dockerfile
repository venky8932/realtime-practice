FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt watcher.py .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "watcher.py"]
