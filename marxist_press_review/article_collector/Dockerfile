FROM python:3.8-slim

WORKDIR /app


COPY requirements.txt /app 
COPY trained_model/ /app

ADD . /app 


RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt


CMD ["python", "guardian_collector.py"]
