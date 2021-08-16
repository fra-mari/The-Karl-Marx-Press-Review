FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app 

RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000
ADD . /app 

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
