FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY aggregator.py aggregator.py

CMD ["python", "aggregator.py"]