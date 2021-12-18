# Create a solo3 Docker image and push to DockerHub

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

## Build solo3 in container

```
  cd ~/git/lrose-bootstrap/docker/solo3
  make_solo3_image.centos
```

This will create an image named:

```
  build.lrose-solo3/centos:latest
```

## Tag the image (no longer needed)

```
   docker tag build.lrose-solo3/centos:latest nsflrose/lrose-solo3:latest
```

## Log in to docker

We want to push the image to nsflrose.

Log in to docker, and ensure you are in the nsflrose group.

```
  docker login
```

## Push the image

```
  docker push nsflrose/lrose-solo3:latest
```

