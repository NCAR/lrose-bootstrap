#!/usr/bin/env python3

#===========================================================================
#
# Checkout and build LROSE, fractl, vortrac and samurai using cmake.
#
# This script performs the following steps:
#
#   1. clone lrose-core from git
#   2. run createCMakeLists.py script to generate CMakeLists.txt files
#   3. run cmake to create Makefiles
#   4. perform the build and install
#   5. check the build
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
from sys import platform

def main():

    # globals

    global thisScriptName
    thisScriptName = os.path.basename(__file__)

    global thisScriptDir
    thisScriptDir = os.path.dirname(__file__)

    global options
    global package

    global releaseName
    global releaseTag
    global releaseDate

    global displaysDir

    global coreDir
    global codebaseDir
    global runtimeLibRelDir

    global prefixDir
    global prefixBinDir
    global prefixLibDir
    global prefixIncludeDir
    global prefixShareDir

    global dateStr
    global logPath
    global logFp

    print("AAAAAAAAAAAAAAAAAAAAAA", file=sys.stderr)

    # parse the command line

    usage = "usage: " + thisScriptName + " [options]"
    homeDir = os.environ['HOME']
    prefixDirDefault = os.path.join(homeDir, 'lrose')
    buildDirDefault = '/tmp/lrose-build'
    logDirDefault = '/tmp/lrose-build/logs'
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
    parser.add_option('--package',
                      dest='package', default='lrose-core',
                      help='Package name. Options are: ' + \
                      'lrose-core (default), lrose-radx, lrose-cidd, apar, samurai')
    parser.add_option('--releaseDate',
                      dest='releaseDate', default='latest',
                      help='Date from which to compute tag for git clone. Applies if --tag is not used.')
    parser.add_option('--tag',
                      dest='tag', default='master',
                      help='Tag to check out lrose. Overrides --releaseDate')
    parser.add_option('--prefix',
                      dest='prefix', default=prefixDirDefault,
                      help='Install directory, default: ' + prefixDirDefault)
    parser.add_option('--buildDir',
                      dest='buildDir', default=buildDirDefault,
                      help='Temporary build dir, default: ' + buildDirDefault)
    parser.add_option('--logDir',
                      dest='logDir', default=logDirDefault,
                      help='Logging dir, default: ' + logDirDefault)
    parser.add_option('--static',
                      dest='static', default=False,
                      action="store_true",
                      help='use static linking, default is dynamic')
    parser.add_option('--installAllRuntimeLibs',
                      dest='installAllRuntimeLibs', default=False,
                      action="store_true",
                      help=\
                      'Install dynamic runtime libraries for all binaries, ' + \
                      'in a directory relative to the bin dir. ' + \
                      'System libraries are included.')
    parser.add_option('--installLroseRuntimeLibs',
                      dest='installLroseRuntimeLibs', default=False,
                      action="store_true",
                      help=\
                      'Install dynamic runtime lrose libraries for all binaries, ' + \
                      'in a directory relative to the bin dir. ' + \
                      'System libraries are not included.')
    parser.add_option('--buildNetcdf',
                      dest='buildNetcdf', default=False,
                      action="store_true",
                      help='Build netcdf and hdf5 from source')
    parser.add_option('--netcdfPrefix',
                      dest='netcdfPrefix', default=prefixDirDefault,
                      help='Netcdf install directory, default: ' + prefixDirDefault)
    parser.add_option('--fractl',
                      dest='build_fractl', default=False,
                      action="store_true",
                      help='Checkout and build fractl after core build is complete')
    parser.add_option('--vortrac',
                      dest='build_vortrac', default=False,
                      action="store_true",
                      help='Checkout and build vortrac after core build is complete')
    parser.add_option('--samurai',
                      dest='build_samurai', default=False,
                      action="store_true",
                      help='Checkout and build samurai after core build is complete')
    parser.add_option('--cmake3',
                      dest='use_cmake3', default=False,
                      action="store_true",
                      help='Use cmake3 instead of cmake')
    parser.add_option('--noApps',
                      dest='noApps', default=False,
                      action="store_true",
                      help='Do not build the lrose core apps')
    parser.add_option('--withJasper',
                      dest='withJasper', default=False,
                      action="store_true",
                      help='Set if jasper library is installed. This provides support for jpeg compression in grib files.')
    parser.add_option('--verboseMake',
                      dest='verboseMake', default=False,
                      action="store_true",
                      help='Verbose output for make, default is summary')
    parser.add_option('--iscray',
                      dest='iscray', default=False,
                      action="store_true",
                      help='True if the Cray compiler is used')
    parser.add_option('--isfujitsu',
                      dest='isfujitsu', default=False,
                      action="store_true",
                      help='True if the Fujitsu compiler is used')
    
    (options, args) = parser.parse_args()
    
    # sanity check: we could not use Cray and Fujitsu compilers at the same time
    assert not (options.iscray and options.isfujitsu), "iscray and isfujitsu could not be both True..."
            
    if (options.verbose):
        options.debug = True

    # check package name

    if (options.package != "lrose-core" and
        options.package != "lrose-radx" and
        options.package != "lrose-cidd" and
        options.package != "apar" and
        options.package != "samurai") :
        print("ERROR: invalid package name: %s:" % options.package, file=sys.stderr)
        print("  options: lrose-core, lrose-radx, lrose-cidd, samurai",
              file=sys.stderr)
        sys.exit(1)

    # For Centos 7, use cmake3

    getOSType()
    if (osId == "centos" and osVersion == "7"):
        options.use_cmake3 = True

    # cmake version

    global cmakeExec
    cmakeExec = 'cmake'
    if (options.use_cmake3):
        cmakeExec = 'cmake3'
    
    # for CIDD, set to static linkage
    if (options.package == "lrose-cidd"):
        options.static = True
        
    package = options.package
    runtimeLibRelDir = package + "_runtime_libs"

    # runtime

    now = time.gmtime()
    nowTime = datetime(now.tm_year, now.tm_mon, now.tm_mday,
                       now.tm_hour, now.tm_min, now.tm_sec)
    dateStr = nowTime.strftime("%Y%m%d")

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
        releaseName = options.package + "-" + dateStr
    else:
        # check we have a good release date
        releaseDate = datetime(int(options.releaseDate[0:4]),
                               int(options.releaseDate[4:6]),
                               int(options.releaseDate[6:8]))
        releaseTag = options.package + "-" + options.releaseDate[0:8]
        releaseName = releaseTag

    # set directories
    
    coreDir = os.path.join(options.buildDir, "lrose-core")
    displaysDir = os.path.join(options.buildDir, "lrose-displays")
    codebaseDir = os.path.join(coreDir, "codebase")

    prefixDir = options.prefix
    prefixBinDir = os.path.join(prefixDir, 'bin')
    prefixLibDir = os.path.join(prefixDir, 'lib')
    prefixIncludeDir = os.path.join(prefixDir, 'include')
    prefixShareDir = os.path.join(prefixDir, 'share')

    # debug print

    if (options.debug):
        print("Running %s:" % thisScriptName, file=sys.stderr)
        print("  osId: ", osId, file=sys.stderr)
        print("  osVersion: ", osVersion, file=sys.stderr)
        print("  package: ", package, file=sys.stderr)
        print("  releaseDate: ", releaseDate, file=sys.stderr)
        print("  releaseName: ", releaseName, file=sys.stderr)
        print("  releaseTag: ", releaseTag, file=sys.stderr)
        print("  static: ", options.static, file=sys.stderr)
        print("  buildDir: ", options.buildDir, file=sys.stderr)
        print("  logDir: ", options.logDir, file=sys.stderr)
        print("  coreDir: ", coreDir, file=sys.stderr)
        print("  codebaseDir: ", codebaseDir, file=sys.stderr)
        print("  displaysDir: ", displaysDir, file=sys.stderr)
        print("  prefixDir: ", prefixDir, file=sys.stderr)
        print("  prefixBinDir: ", prefixBinDir, file=sys.stderr)
        print("  prefixLibDir: ", prefixLibDir, file=sys.stderr)
        print("  prefixIncludeDir: ", prefixIncludeDir, file=sys.stderr)
        print("  prefixShareDir: ", prefixShareDir, file=sys.stderr)
        print("  buildNetcdf: ", options.buildNetcdf, file=sys.stderr)
        print("  verboseMake: ", options.verboseMake, file=sys.stderr)
        print("  use_cmake3: ", options.use_cmake3, file=sys.stderr)
        print("  cmakeExec: ", cmakeExec, file=sys.stderr)
        print("  build_fractl: ", options.build_fractl, file=sys.stderr)
        print("  build_vortrac: ", options.build_vortrac, file=sys.stderr)
        print("  build_samurai: ", options.build_samurai, file=sys.stderr)
        print("  noApps: ", options.noApps, file=sys.stderr)
        print("  iscray: ", options.iscray, file=sys.stderr)
        print("  isfujitsu: ", options.isfujitsu, file=sys.stderr)
        
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

    # run lrose build

    logPath = prepareLogFile("no-logging");
    cmd = os.path.join(thisScriptDir, "lrose_checkout_and_build_cmake.py")
    if (options.clean):
        cmd = cmd + " --clean"
    if (options.debug):
        cmd = cmd + " --debug"
    if (options.verbose):
        cmd = cmd + " --verbose"
    cmd = cmd + " --package " + options.package
    if (options.releaseDate != "latest"):
        cmd = cmd + " --releaseDate " + options.releaseDate
    if (options.tag != "master"):
        cmd = cmd + " --tag " + options.tag
    cmd = cmd + " --prefix " + options.prefix
    cmd = cmd + " --buildDir " + options.buildDir
    cmd = cmd + " --logDir " + options.logDir
    if (options.static):
        cmd = cmd + " --static"
    if (options.installAllRuntimeLibs):
        cmd = cmd + " --installAllRuntimeLibs"
    if (options.installLroseRuntimeLibs):
        cmd = cmd + " --installLroseRuntimeLibs"
    if (options.buildNetcdf):
        cmd = cmd + " --buildNetcdf"
        cmd = cmd + " --netcdfPrefix " + options.netcdfPrefix
    if (options.use_cmake3):
        cmd = cmd + " --cmake3"
    if (options.withJasper):
        cmd = cmd + " --withJasper"
    if (options.verboseMake):
        cmd = cmd + " --verboseMake"
    if (options.iscray):
        cmd = cmd + " --iscray"
    if (options.isfujitsu):
        cmd = cmd + " --isfujitsu"
    shellCmd(cmd)

    # build CSU packages

    if (options.build_fractl):
        logPath = prepareLogFile("build-fractl");
        buildFractl()

    if (options.build_vortrac):
        logPath = prepareLogFile("build-vortrac");
        buildVortrac()

    if (options.build_samurai):
        logPath = prepareLogFile("build-samurai");
        buildSamurai()

    # delete the tmp dir

    if (options.clean):
        shutil.rmtree(options.buildDir)

    logFp.close()
    sys.exit(0)

########################################################################
# build fractl package

def buildFractl():

    print("==>> buildFractl", file=sys.stderr)
    print("====>> prefixDir: ", prefixDir, file=sys.stderr)
    
    # set the environment

    os.environ["LROSE_INSTALL_DIR"] = prefixDir
    
    # check out fractl

    os.chdir(options.buildDir)
    shellCmd("/bin/rm -rf fractl")
    shellCmd("git clone https://github.com/mmbell/fractl")

    # run cmake to create makefiles

    fractlDir = os.path.join(options.buildDir, "fractl");
    cmakeBuildDir = os.path.join(fractlDir, "build")
    os.makedirs(cmakeBuildDir)
    os.chdir(cmakeBuildDir)
    
    cmd = cmakeExec + " -DCMAKE_INSTALL_PREFIX=" + prefixDir + " .."
    shellCmd(cmd)
    
    # do the build and install

    cmd = "make -k -j 8 install/strip"
    if (options.verboseMake):
        cmd = cmd + " VERBOSE=1"
    shellCmd(cmd)

    return

########################################################################
# build vortrac package

def buildVortrac():

    print("====>> buildVortrac", file=sys.stderr)
    print("====>> prefixDir: ", prefixDir, file=sys.stderr)

    # set the environment

    os.environ["LROSE_INSTALL_DIR"] = prefixDir

    # check out vortrac

    os.chdir(options.buildDir)
    shellCmd("/bin/rm -rf vortrac")
    shellCmd("git clone https://github.com/mmbell/vortrac")

    # run cmake to create makefiles

    vortracDir = os.path.join(options.buildDir, "vortrac");
    cmakeBuildDir = os.path.join(vortracDir, "build")
    os.makedirs(cmakeBuildDir)
    os.chdir(cmakeBuildDir)
    
    # run cmake to create makefiles - in-source build
    
    cmd = cmakeExec + " -DCMAKE_INSTALL_PREFIX=" + prefixDir + " .."
    shellCmd(cmd)
    
    # do the build and install
    
    cmd = "make -k -j 8 install/strip"
    if (options.verboseMake):
        cmd = cmd + " VERBOSE=1"
    shellCmd(cmd)
    
    # install resources
    
    os.chdir(vortracDir)

    if (sys.platform == "darwin"):
        os.makedirs("vortrac.app/Contents/Resources")
        cmd = "rsync -av Resources/*.xml vortrac.app/Contents/Resources"
        shellCmd(cmd)

    cmd = "rsync -av Resources " + prefixDir
    shellCmd(cmd)
    
    return

########################################################################
# build samurai package

def buildSamurai():

    print("==>> buildSamurai", file=sys.stderr)
    print("====>> prefixDir: ", prefixDir, file=sys.stderr)

    # set the environment

    os.environ["LROSE_INSTALL_DIR"] = prefixDir
    
    # check out samurai

    os.chdir(options.buildDir)
    shellCmd("/bin/rm -rf samurai")
    shellCmd("git clone https://github.com/mmbell/samurai")
    
    # run cmake to create makefiles - in-source build
    
    samuraiDir = os.path.join(options.buildDir, "samurai");
    cmakeBuildDir = os.path.join(samuraiDir, "build")
    os.makedirs(cmakeBuildDir)
    os.chdir(cmakeBuildDir)

    cmd = cmakeExec + " -DCMAKE_INSTALL_PREFIX=" + prefixDir + " .."
    shellCmd(cmd)

    # do the build and install

    cmd = "make -k -j 8"
    if (options.verboseMake):
        cmd = cmd + " VERBOSE=1"
    cmd = cmd + " install/strip"
    shellCmd(cmd)

    return

########################################################################
# get the OS type from the /etc/os-release file in linux

def getOSType():

    global osId, osVersion
    osId = "unknown"
    osVersion = "unknown"

    if sys.platform == "darwin":
        osId = "darwin"
        return

    if (os.path.exists("/etc/os-release") == False):
        return

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
