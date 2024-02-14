#!/bin/bash                                                                                                                                                                                                                                   

## change to source dir                                                                                                                                                                                                                       
# cd ${SRC_DIR}/code

## compile                                                                                                                                                                                                                                    
# ${CXX} -c hello_world.cc 

## link                                                                                                                                                                                                                                       
# ${CXX} *.o -o hello_world 

g++ hello_world.cc -o hello_world

## install                                                                                                                                                                                                                                    
 mkdir -p /tmp/mytest/bin
 cp hello_world  /tmp/mytest/bin/.
