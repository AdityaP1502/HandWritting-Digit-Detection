FPIC_DIR=src/fpic
LIBS_DIR=src/libs

if [ ! -d "$FPIC_DIR" ];
then 
	echo $FPIC_DIR
	echo "Creating /src/fpic directory"
	mkdir src/fpic
fi

if [ ! -d "$LIBS_DIR" ];
then
	echo "Creating /src/libs directory"
	mkdir src/libs
fi

echo "Building shared library"

echo "Building dynamic array libs"
gcc -c -g -fpic -o src/fpic/dArr.o src/utils/helper/dynamicarray.c
gcc -shared -o src/libs/libdArr.so src/fpic/dArr.o
echo "Build Successfull"

echo "Building error module libs"
gcc -c -g -fpic -o src/fpic/err.o src/utils/helper/error.c
gcc -shared -o src/libs/liberr.so src/fpic/err.o
echo "Building succesful"

echo "Building shape libs"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/shape.o src/utils/helper/shape.c -lerr
gcc -shared -o src/libs/libshape.so src/fpic/shape.o src/fpic/err.o -lm
echo "Build and linking succesful"

echo "Building Hashmap"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/Hashmap.o src/utils/helper/Hashmap.c -ldArr -lerr -lm 
gcc -shared -o src/libs/libHashmap.so src/fpic/Hashmap.o src/fpic/dArr.o src/fpic/err.o -lm
echo "Building and linking hashmap succesfull"

echo "Success"