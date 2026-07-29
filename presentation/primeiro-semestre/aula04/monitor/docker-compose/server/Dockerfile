FROM python:3.12.4 

WORKDIR /app

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt 

COPY . . 

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 