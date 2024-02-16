#!/bin/bash                                                                                                                                                                                                                                   
echo "PWD = " $(PWD)
echo "SRC_DIR = " $SRC_DIR
LROSE_CORE=${SRC_DIR}
echo "LROSE_CORE = " ${LROSE_CORE}
## change to source dir                                                                                                                                                                                                                       

# SRC_DIR is like ... /Users/brenda/miniconda3/conda-bld/my-core2_1694565309776/work
# location of pkgs is /Users/brenda/miniconda3/pkgs/qt-5.15.8-h93fa01e_0.conda
# cd ${SRC_DIR}/code

## compile                                                                                                                                                                                                                                    
# ${CXX} -c hello_world.cc 

## link                                                                                                                                                                                                                                       
# ${CXX} *.o -o hello_world 

# g++ hello_world.cc -o hello_world

## install                                                                                                                                                                                                                                    
 # mkdir -p /tmp/mytest/bin
 # cp hello_world  /tmp/mytest/bin/.

# ---------

export HOST_OS=OSX_LROSE
export LROSE_INSTALL_DIR=/tmp/mylrosetest
# $HOME/lrose
export LROSE_CORE_DIR=${LROSE_CORE}
#  $HOME/git/lrose-core

# Qt path
export CONDA_PKG_DIR=/Users/brenda/miniconda3/pkgs
export QT_PATH=${CONDA_PKG_DIR}/qt-main-5.15.8-hc03889f_16/lib/cmake/Qt5
# export PKG_CONFIG_PATH="/usr/local/opt/qt/lib/pkgconfig"


# trying the old way ...
# cd $LROSE_CORE_DIR/codebase/libs/tdrp/src
# make install
# cd $LROSE_CORE_DIR/codebase/apps/tdrp/src/tdrp_gen
# make install
# cd $LROSE_CORE_DIR/codebase/libs; make  install
# cd $LROSE_CORE_DIR/codebase/build/apps/tdrp/src/tdrp_gen; make -j 8 install
# cd $LROSE_CORE_DIR/codebase/apps; make  install

# this is the cmake way ...
# CONDA_PKG_DIR=/Users/brenda/miniconda3/pkgs
# QT_PATH=${CONDA_PKG_DIR}/qt-main-5.15.8-hc03889f_16/lib/cmake/Qt5
Qt5_DIR=/Users/brenda/miniconda3/pkgs/qt-main-5.15.8-hc03889f_16/lib/cmake/Qt5
cd build/cmake; ./createCMakeLists.py --prefix /tmp/mylrosetest/bin 
cd ${SRC_DIR}/codebase; mkdir build;  cd build;  cmake ..
