# 1. time-tracking

## Installation:

Application is ready to be used in docker.
You need to install it first - https://docs.docker.com/get-docker/.
### Several ways:
#### Production
##### Portainer
1. Install portainer - https://docs.portainer.io/start/install/server/docker/linux
2. Add volume - https://docs.portainer.io/user/docker/volumes/add
3. Create new container - https://docs.portainer.io/user/docker/containers/add, pull image from dockerhub `manascomp/time_tracking`
4. Mount the volume to the container to adress '/database'
##### Raw docker
1. `docker pull manascomp/time_tracking`
2. Addd volume - https://docs.docker.com/storage/volumes/
3. Create new container, pull image from https://hub.docker.com/r/manascomp/time_tracking
4. Mount the volume to the container to adress `/database`
#### Development
##### Raw docker without volume
1. `sh script.sh`
##### Run locally without volume
1. `sh run.sh`
In both cases you can run the 
