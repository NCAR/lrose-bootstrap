#!/usr/bin/env python

#===========================================================================
#
# Run CIDD in docker. Wrapper script.
#
# This script performs the following steps:
#
#   1. clone lrose-core from git
#   2. clone lrose-netcdf from git
#   3. setup autoconf Makefile.am files
#   4. run configure to create makefiles
#   5. perform the build in 32-bit mode, and install
#   6. check the build
#
# You can optionally specify a release date.
#
# Use --help to see the command line options.
#
#===========================================================================

from __future__ import print_function

import os
import sys
from sys import platform
import shutil
import subprocess
from optparse import OptionParser
import time
from datetime import datetime
from datetime import date
from datetime import timedelta

def main():

    global options

    # parse the command line

    thisScriptName = os.path.basename(__file__)
    usage = "usage: " + thisScriptName + " [options]"
    homeDir = os.environ['HOME']
    
    parser = OptionParser(usage)

    parser.add_option('--debug',
                      dest='debug', default=True,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--docker_image',
                      dest='docker_image',
                      default='nsflrose/lrose-cidd',
                      help='Set the docker image to run. Should be in DockerHub.')
    parser.add_option('--params',
                      dest='params',
                      default='',
                      help="Set params file name. For example: 'CIDD.pecan'. In this case the URL would be 'http://front.eol.ucar.edu/displayParams/CIDD.pecan'. i.e. the param file name will be appended to the URL. If the --params option is not used, then the params_url will be used instead.")
    parser.add_option('--params_url',
                      dest='params_url',
                      default='http://front.eol.ucar.edu/displayParams/CIDD.pecan',
                      help='Set the full URL for CIDD params file. This activates if the --params option is not used.')
    parser.add_option('--params_local',
                      dest='params_local',
                      default='',
                      help="Set path of local params file. This will be provided to CIDD running in the container.")

    (options, args) = parser.parse_args()
    
    # check OS - is this a mac?

    global isOsx
    isOsx = False
    if (platform.find("darwin") == 0):
        isOsx = True

    # set DISPLAY string

    if (isOsx):

        # APPLE OSX

        ipAddr = "localhost"
        ifconfig = subprocess.check_output(['ifconfig']).decode('ascii')
        
        for line in ifconfig.split("\n"):
            if ((line.find("127.0.0.1") < 0) and
                line.find("inet ") >= 0):
                ipaddr = line.split()[1]
        print("ipAddr: ", ipAddr, file=sys.stderr)

        displayNum = ":0"
        ps = subprocess.check_output(['ps', '-e']).decode('ascii')
        for line in ps.split("\n"):
            if ((line.find("xinit") < 0) and
                (line.find("Xquartz") >= 0) and
                (line.find("listen") >= 0)):
                displayNum = line.split()[4]

        displayStr = "-e DISPLAY=" + ipaddr + displayNum

    else:

        # LINUX

        displayStr = "-e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix"

    # debug

    if (options.debug):
        print("Running %s:" % thisScriptName, file=sys.stderr)
        print("  docker image: ", options.docker_image, file=sys.stderr)
        print("  CIDD params URL: ", options.params_url, file=sys.stderr)
        if (isOsx):
            print("  OS: this is a mac", file=sys.stderr)
        else:
            print("  OS: this is NOT a mac", file=sys.stderr)
        print("  displayStr: ", displayStr, file=sys.stderr)

    # for local params make copy into /tmp

    paramsLocal = False
    localName = os.path.basename(options.params_local)
    tmpDir = "/tmp/cidd_params"
    if (len(options.params_local) > 0):
        paramsLocal = True
        try:
            os.makedirs(tmpDir)
        except:
            if (options.verbose):
                print("Info exists: ", tmpDir, file=sys.stderr)
        shellCmd("rsync -av " + options.params_local + " " + tmpDir)

    # set up call for running docker
    
    cmd = "docker run -v $HOME/.Xauthority:/root/.Xauthority "
    cmd += "-v /tmp/cidd_images:/root/images "
    if (paramsLocal):
        cmd += "-v /tmp/cidd_params:/root/params "
    cmd += displayStr + " "
    cmd += options.docker_image + " "
    cmd += "/usr/local/cidd/bin/CIDD -font fixed -p "
    if (paramsLocal):
        cmd += "/root/params/" + localName
    elif (len(options.params) > 0):
        cmd += "http://front.eol.ucar.edu/displayParams/" + options.params
    else:
        cmd += options.params_url
    if (options.verbose):
        cmd += " -v 2"

    # run the command

    shellCmd(cmd)

    # exit

    sys.exit(0)

########################################################################
# Run a command in a shell, wait for it to complete

def shellCmd(cmd):

    print("Running cmd:", cmd, file=sys.stderr)
    
    try:
        retcode = subprocess.check_call(cmd, shell=True)
        if retcode != 0:
            print("Child exited with code: ", retcode, file=sys.stderr)
            sys.exit(1)
        else:
            if (options.verbose):
                print("Child returned code: ", retcode, file=sys.stderr)

    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        sys.exit(1)

    print("    done", file=sys.stderr)
    
########################################################################
# Run - entry point

if __name__ == "__main__":
   main()
