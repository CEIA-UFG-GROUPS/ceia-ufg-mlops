FROM python:3.10.14-slim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

CMD ["python", "-m", "streamlit", "run", "app.py"]