docker build -t ondrejman/flaskr:latest . 

docker container run -d  --name time_tracking -p 4995:4995 ondrejman/flaskr    