# Building RPM packages for RedHat-type OSs (RHEL, CENTOS, FEDORA)

## Building RPMS using docker

We use docker containers to build the RPMs for various RedHat versions of LINUX.

To make use of these you will need to install docker.

These builds have been tested on the following versions:

  * centos 7
  * centos 8
  * centos latest (stream)
  * fedora 27
  * fedora 28
  * fedora 29
  * fedora 30
  * fedora 31
  * fedora 32
  * fedora 33

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
  custom/centos:7
```

### Perform the lrose build: run ```do_lrose_build.redhat```.

Perform the build in the custom container.

This creates a new container, that will be called, as an example:

```
  build.lrose-core/centos:7
```

### Create the rpm: run ```make_package.redhat```.

This will create the rpm from the build, and store it in, as an example:

```
  /tmp/pkg.centos_7.lrose-core/lrose-core-20210217-centos_7.x86_64.rpm
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
  /tmp/pkg.centos_7.lrose-core/lrose-core.centos_7.install_log.txt
```

The length of the log file should be over 5000 bytes.

If it is shorter than this, it is likely that an error occurred. Check the log file to see what went wrong.

## Location of RPMs

The RPMs are built in the containers, and then copied across onto cross-mounted locations on the host.

After the RPMs are built they are placed in /tmp.

For example:

```
  /tmp/pkg.centos_7.lrose-core/lrose-core-20210217-centos_7.x86_64.rpm
  /tmp/pkg.centos_8.lrose-core/lrose-core-20210217-centos_8.x86_64.rpm
  /tmp/pkg.centos_latest.lrose-core/lrose-core-20210217-centos_latest.x86_64.rpm
  /tmp/pkg.fedora_31.lrose-core/lrose-core-20210217-fedora_31.x86_64.rpm
  /tmp/pkg.fedora_31.lrose-core/lrose-core-20210217-fedora_32.x86_64.rpm
  /tmp/pkg.fedora_31.lrose-core/lrose-core-20210217-fedora_33.x86_64.rpm
```

These are also copied into the release directory:

```
  $HOME/releases/lrose-core
```

## Installing the RPMs on a host system

You use yum to install the RPMs on your host.

For RHEL and CENTOS, you first need to install epel-release:

```
  yum install -y epel-release
```

This step is not needed for fedora.

The use yum to install the RPM. For example:

```
  yum install -y ./lrose-core-20210217-centos_7.x86_64.rpm
```

Note that you need to specify the absolute path, hence the '.'.

  

