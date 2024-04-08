# run in docker because I need root permission to install packages.
#FROM python:3
# FROM alpine:latest # alpine does not seem to be sufficient
# Ensure that basic utilities are installed. We need curl and tar with support for bzip2. Also you need a glibc based system like Ubuntu, Fedora or Centos (Alpine Linux does not work natively).
# Rocky Linux is centos
FROM rockylinux:8.9
# or try ...
# docker run -it --rm mambaorg/micromamba:latest micromamba info



# ENV SHELL=/bin/sh
# ENV PYTHONUNBUFFERED=1

# install python (as needed)
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN yum -y  update && yum install -y git python3 curl bzip2 wget
# RUN apk add curl git 


# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . . 

RUN useradd  -ms /bin/sh gucci

USER gucci
WORKDIR /home/gucci

USER gucci


