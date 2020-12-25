FROM python:3.6
ENV PYTHONUNBUFFERED=1
WORKDIR /code3
COPY requirements.txt /code3/
RUN pip install -r requirements.txt
COPY . /code3/