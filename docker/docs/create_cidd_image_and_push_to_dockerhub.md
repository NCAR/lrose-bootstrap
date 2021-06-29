# Create a CIDD Docker image and push to DockerHub

## Clone lrose-bootstrap repo

```
  mkdir ~/git
  cd ~/git
  git clone https://github.com/ncar/lrose-bootstrap
```

## Make sure the custom Centos 7 image exists

```
  cd ~/git/lrose-bootstrap/docker
  ./redhat/make_custom_image.redhat -t centos -v 7
```

## Build CIDD in container

```
  cd ~/git/lrose-bootstrap/docker/cidd
  make_cidd_image.centos
```

This will create an image named:

```
  build.lrose-cidd/centos:latest
```

## Tag the image

```
   docker tag build.lrose-cidd/centos:latest nsflrose/lrose-cidd:latest
```

## Log in to docker

We want to push the image to nsflrose.

Log in to docker, and ensure you are in the nsflrose group.

```
  docker login
```

## Push the image

```
  docker push nsflrose/lrose-cidd:latest
```

