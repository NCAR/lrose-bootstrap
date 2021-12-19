#!/usr/bin/env python

#===========================================================================
#
# Run solo3 in docker. Wrapper script.
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

    # get current dir

    thisDir = os.getcwd()

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
    parser.add_option('--dir',
                      dest='dir', default=thisDir,
                      help='Directory containing the DORADE data. Default is the current directory.')
    parser.add_option('--docker_image',
                      dest='docker_image',
                      default='nsflrose/lrose-solo3',
                      help='Set the docker image to run. Should be in DockerHub. Default is "nsflrose/lrose-solo3"')

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
        ifconfig = subprocess.check_output(['ifconfig'])
        for line in ifconfig.split("\n"):
            if ((line.find("127.0.0.1") < 0) and
                line.find("inet ") >= 0):
                ipaddr = line.split()[1]
        print("ipAddr: ", ipAddr, file=sys.stderr)

        displayNum = ":0"
        ps = subprocess.check_output(['ps', '-e'])
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

    dataDir = options.dir
    if (dataDir.find('.') >= 0):
        dataDir = thisDir

    if (options.debug):
        print("Running %s:" % thisScriptName, file=sys.stderr)
        print("  docker image: ", options.docker_image, file=sys.stderr)
        if (isOsx):
            print("  OS: this is a mac", file=sys.stderr)
        else:
            print("  OS: this is NOT a mac", file=sys.stderr)
        print("  displayStr: ", displayStr, file=sys.stderr)
        print("  dataDir: ", dataDir, file=sys.stderr)

    # get the sweep files in a list

    sweepList = " "
    allFiles = os.listdir(dataDir)
    for file in allFiles:
        if (file.find("swp.") == 0):
            sweepList = sweepList + " ./" + file
    print("  sweepList: ", sweepList, file=sys.stderr)

    # set up call for running docker
    
    cmd = "docker run -v $HOME/.Xauthority:/root/.Xauthority "
    cmd += "-v " + dataDir + ":/data "
    cmd += displayStr + " "
    cmd += options.docker_image + " "
    bashcmd = "cd /data; /usr/local/bin/solo3 -f " + sweepList
    cmd += 'bash -c \"' + bashcmd + '\"'

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
