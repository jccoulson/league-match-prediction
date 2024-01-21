FROM python:3.8

#environmental vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#working dir
WORKDIR /app

#get dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/

#collect static because in production cannot use static dir
RUN python manage.py collectstatic --noinput

#run app
CMD gunicorn leaguepred.wsgi:application --bind 0.0.0.0:8000
