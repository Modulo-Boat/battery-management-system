FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY metrics.py .
COPY app.py .

EXPOSE 5000
EXPOSE 9090

CMD ["python3", "app.py"]