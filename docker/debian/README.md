# Building .deb package files for Debian-based OS versions (debian, ubuntu)

## Building .deb package files for LROSE using docker

We use Docker containers to build the .deb package files for various Debian-based versions of LINUX.

To make use of these you will need to install docker.

These builds have been tested on the following versions:

  * debian 9
  * debian 10
  * ubuntu 16.04
  * ubuntu 18.04
  * ubuntu 20.04

## Steps in the process

The following are the steps required in the process:

| Step      | Script to run  |
| --------- | -------------  |
| Create custom container | ```make_custom_image.debian``` |
| Perform the lrose build | ```do_lrose_build.debian``` |
| Create the package | ```make_package.debian``` |
| Install and test the package | ```install_pkg_and_test.debian``` |

The details of the steps are as follows:

### Create custom container: run ```make_custom_image.debian```.

Create a container, based on the OS image, with the relevant packages installed.

The created container will be called, as an example:

```
  custom/debian:10
```

### Perform the lrose build: run ```do_lrose_build.debian```.

Perform the build in the custom container.

This creates a new container, that will be called, as an example:

```
  build.lrose-core/debian:10
```

### Create the rpm: run ```make_package.debian```.

This will create the rpm from the build, and store it in, as an example:

```
  /tmp/pkg.centos_7.lrose-core/lrose-core-20210217-debian_10.amd64.deb
```

with a copy in

```
  $HOME/releases/lrose-core
```

### Install and test the deb: run ```install_pkg_and_test.debian```.

For the test step, the DEB file is installed into a clean container, and one of the applications is run to make sure the installation was successful.

The command we run as a test is:

```
  RadxPrint -h
```

On success this will create a log file with the output from ```RadxPrint```.

The log file will be, as an example:

```
  /tmp/pkg.debian_10.lrose-core/lrose-core.debian_10.install_log.txt
```

The length of the log file should be over 5000 bytes.

If it is shorter than this, it is likely that an error occurred. Check the log file to see what went wrong.

## Location of DEB files

The DEB files are built in the containers, and then copied across onto cross-mounted locations on the host.

After the DEBs are built they are placed in /tmp.

For example:

```
  /tmp/pkg.debian_9.lrose-core/lrose-core-20210217-debian_9.amd64.deb
  /tmp/pkg.debian_10.lrose-core/lrose-core-20210217-debian_10.amd64.deb
  /tmp/pkg.ubuntu_16.04.lrose-core/lrose-core-20210217-ubuntu_16.04.amd64.deb
  /tmp/pkg.ubuntu_18.04.lrose-core/lrose-core-20210217-ubuntu_18.04.amd64.deb
  /tmp/pkg.ubuntu_20.04.lrose-core/lrose-core-20210217-ubuntu_20.04.amd64.deb
```

These are also copied into the release directory:

```
  $HOME/releases/lrose-core
```

## Installing the DEB file on a host system

You use apt-get to install the DEB file on your host.

```
  apt-get update
  apt-get install -y ./lrose-core-20210217-debian_10.amd64.deb
```

Note that you need to specify the absolute path, hence the '.'.
