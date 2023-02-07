FROM python:3.8.2-alpine3.11

ENV FLASK_APP=flaskr
ENV FLASK_ENV=development

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN flask init-db

#Unit tests
#RUN pip install pytest && pytest

EXPOSE 4995

CMD [ "flask", "--debug", "run", "--host=0.0.0.0", "--port=4995" ]