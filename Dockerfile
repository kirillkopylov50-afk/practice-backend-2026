FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN touch /app/.init_done || python init_db.py

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]