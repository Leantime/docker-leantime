FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV LEANTIME_BASE_URL=http://192.168.2.48:8080
ENV LEANTIME_API_KEY=""

EXPOSE 8000

CMD ["python", "server.py"]
