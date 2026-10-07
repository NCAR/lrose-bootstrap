# Building RPM packages for RedHat-based OSs (RHEL, CENTOS, FEDORA)

## Building RPMS using Docker

We use Docker containers to build the RPMs for various RedHat versions of LINUX.

To make use of these you will need to install docker.

These builds have been tested on the following versions:

  * centos 7, 8
  * almalinux 9, 10
  * rockylinux 9, 10
  * fedora 27 - 45

## Steps in the process

The following are the steps required in the process:

| Step      | Script to run  |
| --------- | -------------  |
| Create custom container | ```make_custom_image.redhat``` |
| Perform the lrose build | ```do_lrose_build.redhat``` |
| Create the rpm | ```make_package.redhat``` |
| Install and test the rpm | ```install_pkg_and_test.redhat``` |

The details of the steps are as follows:

### Create custom container: run ```make_custom_image.redhat```.

Create a container, based on the OS image, with the relevant packages installed.

The created container will be called, as an example:

```
  custom/almalinux:10
```

### Perform the lrose build: run ```do_lrose_build.redhat```.

Perform the build in the custom container.

This creates a new container, that will be called, as an example:

```
  build.lrose-core/almalinux:10
```

### Create the rpm: run ```make_package.redhat```.

This will create the rpm from the build, and store it in, as an example:

```
  $HOME/releases/lrose-core/pkg.almalinux_10.lrose-core/lrose-core-20261006-almalinux_10.x86_64.rpm
```

with a copy in

```
  $HOME/releases/lrose-core
```

### Install and test the rpm: run ```install_pkg_and_test.redhat```.

For the test step, the RPM is installed into a clean container, and one of the applications is run to make sure the installation was successful.

The command we run as a test is:

```
  RadxPrint -h
```

On success this will create a log file with the output from ```RadxPrint```.

The log file will be, as an example:

```
  $HOME/releases/lrose-core/pkg.almalinux_10.lrose-core/lrose-core.almalinux_10.install_log.txt
```

The length of the log file should be over 5232 bytes.

If it is shorter than this, it is likely that an error occurred. Check the log file to see what went wrong.

## Installing the RPMs on a host system

You can download the rpms from lrose-core/releases on GitHub.

You use dnf to install the RPMs on your host.

For RHEL and CENTOS, you first need to install epel-release:

```
  dnf install -y epel-release
```

This step is not needed for fedora.

The use dnf to install the RPM. For example:

```
  dnf install -y ./lrose-core-20261006-almalinux_10.x86_64.rpm
```

Note that you need to specify the absolute path, hence the '.'.

  

