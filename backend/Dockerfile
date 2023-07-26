FROM python:3.9.13-slim

WORKDIR /backend

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD python manage.py collectstatic --noinput && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 foodgram.wsgi:application --reload