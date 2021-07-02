#!/usr/bin/env python

#===========================================================================
#
# Checkout and build solo3, using autoconf/automake and configure.
#
# This script performs the following steps:
#
#   1. clone lrose-solo3 from git
#   2. run configure to create makefiles
#   3. perform the build and install
#   4. check the build
#
# You can optionally specify a release date.
#
# Use --help to see the command line options.
#
#===========================================================================

from __future__ import print_function
import os
import sys
import shutil
import subprocess
from optparse import OptionParser
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import glob

def main():

    # globals

    global options

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

    global thisScriptDir
    thisScriptDir = os.path.dirname(__file__)

    global package
    package = 'solo3'

    global releaseName
    global releaseTag
    global releaseDate

    global solo3Dir
    global runtimeLibRelDir

    global prefixDir
    global prefixBinDir
    global prefixLibDir
    global prefixIncludeDir

    global dateStr
    global logPath
    global logFp

    # parse the command line

    usage = "usage: " + thisScriptName + " [options]"
    homeDir = os.environ['HOME']
    prefixDirDefault = '/tmp/solo3-install'
    buildDirDefault = '/tmp/solo3-build'
    logDirDefault = '/tmp/solo3-build/logs'
    parser = OptionParser(usage)
    parser.add_option('--clean',
                      dest='clean', default=False,
                      action="store_true",
                      help='Cleanup tmp build dir')
    parser.add_option('--debug',
                      dest='debug', default=True,
                      action="store_true",
                      help='Set debugging on')
    parser.add_option('--verbose',
                      dest='verbose', default=False,
                      action="store_true",
                      help='Set verbose debugging on')
    parser.add_option('--releaseDate',
                      dest='releaseDate', default='latest',
                      help='Date from which to compute tag for git clone. Applies if --tag is not used.')
    parser.add_option('--tag',
                      dest='tag', default='master',
                      help='Tag to check out solo3. Overrides --releaseDate')
    parser.add_option('--prefix',
                      dest='prefix', default=prefixDirDefault,
                      help='Install directory, default: ' + prefixDirDefault)
    parser.add_option('--buildDir',
                      dest='buildDir', default=buildDirDefault,
                      help='Temporary build dir, default: ' + buildDirDefault)
    parser.add_option('--logDir',
                      dest='logDir', default=logDirDefault,
                      help='Logging dir, default: ' + logDirDefault)
    parser.add_option('--installRuntimeLibs',
                      dest='installRuntimeLibs', default=False,
                      action="store_true",
                      help=\
                      'Install dynamic runtime libraries for all binaries, ' + \
                      'in a directory relative to the bin dir. ' + \
                      'System libraries are included.')
    parser.add_option('--static',
                      dest='static', default=False,
                      action="store_true",
                      help='use static linking, default is dynamic')
    (options, args) = parser.parse_args()
    
    if (options.verbose):
        options.debug = True

    runtimeLibRelDir = package + "_runtime_libs"

    # runtime

    now = time.gmtime()
    nowTime = datetime(now.tm_year, now.tm_mon, now.tm_mday,
                       now.tm_hour, now.tm_min, now.tm_sec)
    dateStr = nowTime.strftime("%Y%m%d")

    # check OS type

    getOSType()

    # set release tag

    if (options.tag != "master"):
        releaseTag = options.tag
        releaseName = options.tag
        releaseDate = "not-set"
    elif (options.releaseDate == "latest"):
        releaseDate = datetime(int(dateStr[0:4]),
                               int(dateStr[4:6]),
                               int(dateStr[6:8]))
        releaseTag = "master"
        releaseName = package + "-" + dateStr
    else:
        # check we have a good release date
        releaseDate = datetime(int(options.releaseDate[0:4]),
                               int(options.releaseDate[4:6]),
                               int(options.releaseDate[6:8]))
        releaseTag = package + "-" + options.releaseDate[0:8]
        releaseName = releaseTag

    # set directories
    
    solo3Dir = os.path.join(options.buildDir, "lrose-solo3")

    prefixDir = options.prefix
    prefixBinDir = os.path.join(prefixDir, 'bin')
    prefixLibDir = os.path.join(prefixDir, 'lib')
    prefixIncludeDir = os.path.join(prefixDir, 'include')

    # debug print

    if (options.debug):
        print("Running %s:" % thisScriptName, file=sys.stderr)
        print("  osId: ", osId, file=sys.stderr)
        print("  osVersion: ", osVersion, file=sys.stderr)
        print("  solo3Dir: ", solo3Dir, file=sys.stderr)
        print("  releaseDate: ", releaseDate, file=sys.stderr)
        print("  releaseName: ", releaseName, file=sys.stderr)
        print("  releaseTag: ", releaseTag, file=sys.stderr)
        print("  static: ", options.static, file=sys.stderr)
        print("  buildDir: ", options.buildDir, file=sys.stderr)
        print("  logDir: ", options.logDir, file=sys.stderr)
        print("  prefixDir: ", prefixDir, file=sys.stderr)
        print("  prefixBinDir: ", prefixBinDir, file=sys.stderr)
        print("  prefixLibDir: ", prefixLibDir, file=sys.stderr)
        print("  prefixIncludeDir: ", prefixIncludeDir, file=sys.stderr)

    # create build dir
    
    createBuildDir()

    # initialize logging

    if (os.path.isdir(options.logDir) == False):
        os.makedirs(options.logDir)
    logPath = os.path.join(options.logDir, "initialize");
    logFp = open(logPath, "w+")
    
    # make dirs

    try:
        os.makedirs(prefixDir)
        os.makedirs(prefixBinDir)
        os.makedirs(prefixLibDir)
        os.makedirs(prefixIncludeDir)
        os.makedirs(options.logDir)
    except:
        print("  note - dirs already exist", file=sys.stderr)

    # get repos from git

    logPath = prepareLogFile("git-checkout");
    gitCheckout()

    # build the package

    buildPackage()

    # detect which dynamic libs are needed
    # copy the dynamic libraries into a directory relative
    # to the binary install dir:
    #     bin/${package}_runtime_libs

    os.chdir(solo3Dir)
    if (options.installRuntimeLibs):
        scriptPath = "./installOriginLibFiles.py"
        cmd = scriptPath + \
              " --binDir " + prefixBinDir + \
              " --relDir " + runtimeLibRelDir
        if (options.debug):
            cmd = cmd + " --debug"
        shellCmd(cmd)

    # finalize the install

    logPath = prepareLogFile("do-final-install");
    doFinalInstall();

    # check the install

    logPath = prepareLogFile("no-logging");
    checkInstall()

    # delete the tmp dir

    if (options.clean):
        shutil.rmtree(options.buildDir)

    logFp.close()
    sys.exit(0)

########################################################################
# create the build dir

def createBuildDir():

    # check if exists already

    if (os.path.isdir(options.buildDir)):

        print("WARNING: you are about to remove all contents in dir: " + 
              options.buildDir)
        print("===============================================")
        contents = os.listdir(options.buildDir)
        for filename in contents:
            print(("  " + filename))
        print("===============================================")
        answer = "n"
        if (sys.version_info > (3, 0)):
            answer = input("WARNING: do you wish to proceed (y/n)? ")
        else:
            answer = raw_input("WARNING: do you wish to proceed (y/n)? ")
        if (answer != "y"):
            print("  aborting ....")
            sys.exit(1)
                
        # remove it

        shutil.rmtree(options.buildDir)

    # make it clean
    
    print(("INFO: you are about to create build dir: " + 
          options.buildDir))
    
    os.makedirs(options.buildDir)

########################################################################
# check out repos from git

def gitCheckout():

    os.chdir(options.buildDir)

    shellCmd("/bin/rm -rf lrose-solo3")
    if (options.tag == "master"):
        shellCmd("git clone https://github.com/NCAR/lrose-solo3")
    else:
        shellCmd("git clone --branch " + releaseTag + \
                 " https://github.com/NCAR/lrose-solo3")

########################################################################
# build package

def buildPackage():

    global logPath

    # set the environment

    os.environ["LDFLAGS"] = "-L" + prefixLibDir + " " + \
                            "-Wl,--enable-new-dtags," + \
                            "-rpath," + \
                            "'$$ORIGIN/" + runtimeLibRelDir + \
                            ":$$ORIGIN/../lib" + \
                            ":" + prefixLibDir + \
                            ":" + prefixLibDir + "'"

    os.environ["FC"] = "gfortran"
    os.environ["F77"] = "gfortran"
    os.environ["F90"] = "gfortran"

    if (sys.platform == "darwin"):
        os.environ["PKG_CONFIG_PATH"] = "/usr/local/opt/qt/lib/pkgconfig"
    else:
        os.environ["CXXFLAGS"] = " -std=c++11 "

    # print out environment

    logPath = prepareLogFile("print-environment");
    cmd = "env"
    shellCmd(cmd)

    # run autoconf

    os.chdir(solo3Dir)
    logPath = prepareLogFile("run-autoconf");
    if (options.static):
        cmd = "./runAutoConf.py --dir ."
    else:
        cmd = "./runAutoConf.py --dir . --shared"
    shellCmd(cmd)

    # run configure

    os.chdir(solo3Dir)
    logPath = prepareLogFile("run-configure");
    cmd = "./configure --prefix=" + prefixDir
    shellCmd(cmd)

    # do the build

    logPath = prepareLogFile("build-apps");
    cmd = "make -j 8"
    shellCmd(cmd)

    # do the install

    cmd = "make -k install"
    shellCmd(cmd)

########################################################################
# perform final install

def doFinalInstall():

    # install docs etc
    
    os.chdir(solo3Dir)

    shellCmd("rsync -av LICENSE.txt " + prefixDir)
    shellCmd("rsync -av VERSION " + prefixDir)
    
########################################################################
# check the install

def checkInstall():

    os.chdir(solo3Dir)
    print(("============= Checking install for " + package + " apps ============="))
    shellCmd("./checkSolo3Install.py" + \
                 " --prefix " + prefixDir)
    print("====================================================")
    
    print("**************************************************")
    print("*** Done building auto release *******************")
    print(("*** Installed in dir: " + prefixDir + " ***"))
    print("**************************************************")

########################################################################
# get the OS type from the /etc/os-release file in linux

def getOSType():

    global osId, osVersion
    osId = ""
    osVersion = ""

    osrelease_file = open("/etc/os-release", "rt")
    lines = osrelease_file.readlines()
    osrelease_file.close()
    for line in lines:
        if (line.find('ID=') == 0):
            osId = line.split('=')[1].replace('"', '').strip()
        elif (line.find('VERSION_ID=') == 0):
            osVersion = line.split('=')[1].replace('"', '').strip()

########################################################################
# prepare log file

def prepareLogFile(logFileName):

    global logFp

    logFp.close()
    logPath = os.path.join(options.logDir, logFileName + ".log");
    if (logPath.find('no-logging') >= 0):
        return logPath
    print("========================= " + logFileName + " =========================", file=sys.stderr)
    if (options.verbose):
        print("====>> Creating log file: " + logPath + " <<==", file=sys.stderr)
    logFp = open(logPath, "w+")
    logFp.write("===========================================\n")
    logFp.write("Log file from script: " + thisScriptName + "\n")
    logFp.write(logFileName + "\n")

    return logPath

########################################################################
# Run a command in a shell, wait for it to complete

def shellCmd(cmd):

    print("Running cmd:", cmd, file=sys.stderr)
    
    if (options.verbose):
        cmdToRun = cmd
    elif (logPath.find('no-logging') >= 0):
        cmdToRun = cmd
    else:
        print("Log file is:", logPath, file=sys.stderr)
        print("    ....", file=sys.stderr)
        cmdToRun = cmd + " 1>> " + logPath + " 2>&1"

    try:
        retcode = subprocess.check_call(cmdToRun, shell=True)
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
