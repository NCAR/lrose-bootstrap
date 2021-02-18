# Creating .rpm and .deb packages using Docker

This docker directory contains the scripts and Dockerfiles needed to build packages for the various flavors of the LINUX operating system.

## Making the packages

There are 4 steps to this process:

1. Create custom containers
2. Perform the builds
3. Make the package files
4. Install and test the packages

## Detailed docs for each OS

| LINUX flavor | Versions |
| ------ |:----------------:|
| [redhat](./redhat/README.md) | Centos, Fedora, RHEL |
| [debian](./debian/README.md)   | Debian, Ubuntu |
| [suse](./suse/README.md)  | OpenSuse |
| [oracle](./oracle/README.md)  | OracleLinux |

## High-level scripts

The following high-level scripts are provided:

* ```make_custom_images```: create the custom docker images for each OS version

* ```perform_builds```: run the build for each OS version

* ```make_packages```: make the .rpm and .deb files for each OS version

* ```install_and_test_packages```: install each package file in a clean container, and run RadxPrint to check that the apps will run

* ```remove_running_containers```: remove any containers that are currently running

* ```delete_images.build```: delete docker images from the build step

* ```delete_images.custom```: delete docker images from the customize step

