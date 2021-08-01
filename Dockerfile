# docker build -t ubuntu1604py36
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4455

CMD [ "python", "./app.py" ]
