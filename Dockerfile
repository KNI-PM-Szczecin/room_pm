FROM python:3.14-slim

WORKDIR /roompm

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start bota
CMD ["python", "main.py"]
LABEL authors="zekq"
