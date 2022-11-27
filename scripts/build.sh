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
echo "Build dynamic array uccessfull"

echo "Building error module libs"
gcc -c -g -fpic -o src/fpic/err.o src/utils/helper/error.c
gcc -shared -o src/libs/liberr.so src/fpic/err.o
echo "Building error module succesful"

echo "Building sort modules libs"
gcc -c -g -fpic -o src/fpic/sort.o src/utils/helper/sort.c -lerr
gcc -shared -o src/libs/libsort.so src/fpic/sort.o src/fpic/err.o
echo "Build and link sort libs successful"

echo "Building stack libs"
gcc -c -g -fpic -o src/fpic/stack.o src/utils/helper/stack.c -lerr
gcc -shared -o src/libs/libstack.so src/fpic/stack.o src/fpic/err.o
echo "Building and linking stack successful"

echo "Building image libs"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/image.o src/utils/image/image.c -lerr
gcc -shared -o src/libs/libimage.so src/fpic/image.o src/fpic/err.o
echo "Build and linking image succesful"

echo "Building hashmap"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/hashmap.o src/utils/helper/hashmap.c -ldArr -lerr 
gcc -shared -o src/libs/libhashmap.so src/fpic/hashmap.o src/fpic/dArr.o src/fpic/err.o
echo "Building and linking hashmap succesfull"

echo "Building shape libs"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/shape.o src/utils/helper/shape.c -lhashmap -ldArr -lerr -lm
gcc -shared -o src/libs/libshape.so src/fpic/shape.o src/fpic/hashmap.o src/fpic/dArr.o src/fpic/err.o -lm
echo "Build and linking shape succesful"

echo "Building bbox"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/bbox.o src/utils/image/bbox.c -lhashmap -ldArr -limage -lshape -lerr
gcc -shared -o src/libs/libbbox.so src/fpic/bbox.o src/fpic/hashmap.o src/fpic/dArr.o src/fpic/image.o src/fpic/shape.o src/fpic/err.o
echo "Building and linking bbox succesful"

echo "Building thresh"
gcc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/thresh.o src/utils/image/thresh.c -limage  -lerr
gcc -shared -o src/libs/libthresh.so src/fpic/thresh.o src/fpic/image.o src/fpic/err.o 
echo "Building and linking thresh succesful"

echo "building loop_enhancer"
cc -g -c -fpic -Wall -Lsrc/libs -Wl,-rpath=src/libs -o src/fpic/enhancer.o src/utils/image/loop_enhancer.c -limage  -lstack -lerr
gcc -shared -o src/libs/libenhancer.so src/fpic/enhancer.o src/fpic/image.o src/fpic/stack.o src/fpic/err.o 
echo "Building and linking loop enhancer succesful"
echo "Success"