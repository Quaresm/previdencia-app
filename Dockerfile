FROM python:3.8-alpine3.12

EXPOSE 5000

ENV PYTHONUNBUFFERED 1

RUN apk update
#RUN apk add build-base libressl libffi-dev libressl-dev libxslt-dev libxml2-dev xmlsec-dev xmlsec
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools wheel

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python", "app/main.py"]

#ENTRYPOINT gunicorn app.main:app --bind 127.0.0.1:5000
