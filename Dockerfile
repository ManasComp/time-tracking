FROM python:3-alpine3.15

WORKDIR /app

COPY . /app/
RUN pip3 install -r requirements.txt

EXPOSE 4998 

CMD flask --app flaskr --debug run --host=0.0.0.0 -p 4998 