# Version: 0.0.1
# Bot Docker file!
FROM python:3.6-jessie
MAINTAINER Mike Shenin <i@kotrik.ru>

WORKDIR /usr/app
COPY . /usr/app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./run.py"]
