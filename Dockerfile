# docker build -t ubuntu1604py36
FROM ubuntu:16.04

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 4455

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
