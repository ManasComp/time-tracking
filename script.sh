sudo docker stop time_tracking

sudo docker rm time_tracking

docker build -t ondrejman/flaskr:latest . 

docker container run -d  --name time_tracking -p 4995:4995 ondrejman/flaskr 

docker logs time_tracking