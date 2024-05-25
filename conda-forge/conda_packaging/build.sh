#!/bin/bash                                                                                                                                                                                                                                   
${BUILD_PREFIX}/bin/cmake \
	-H${SRC_DIR} \
	-Bmybuild \
	-DCMAKE_INSTALL_PREFIX=${PREFIX} \
	codebase

cd mybuild
make
make install


echo "after make install for lrose-core"

rm -rf mybuild
rm -rf ${SRC_DIR}/codebase

echo "last line of build.sh"

