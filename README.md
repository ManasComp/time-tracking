# Time Tracking

## Installation:

Application is ready to be used in docker.
You need to install docker first - https://docs.docker.com/get-docker/.
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
1. Clone this repository
##### Raw docker without volume
2. `sh script.sh`
##### Run locally without volume
2. `sh run.sh`
### Minimal requirements
- system that supports docker engine
- connection to internet
- at least 8GB RAM
- at least 5GB free storage on  SSD
### How to access
#### default admin user
- username: `Ondrej`
- password: `Man`
#### From docker
- address `localhost:4995`
#### Locally
- address `localhost:4999`

