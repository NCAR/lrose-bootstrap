# lrose-bootstrap

The lrose-bootstrap repository contains:

* scripts for checking out and building LROSE.
* docker scripts for creating .rpm and .deb package files. 

This is a small repository that is quick to check out.

## Checkout and build lrose-core using cmake

Run:

```
  checkout_and_build_cmake.py
```

to clone lrose core from github, build it using ```cmake``` in a temporary location, and install it.

Run:

```
  checkout_and_build_cmake.py --help
```

for the usage.

## Checkout and build lrose-core using automake

Run:

```
  checkout_and_build_auto.py
```

to clone lrose core from github, build it using ```configure``` in a temporary location, and install it.

Run:

```
  checkout_and_build_auto.py --help
```

for the usage.

## Create packages using Docker

See: [Creating packages](./docker/README.md)

## Build CIDD and push CIDD image to DockerHub

See: [Build CIDD](./docker/docs/create_cidd_image_and_push_to_dockerhub.md)

