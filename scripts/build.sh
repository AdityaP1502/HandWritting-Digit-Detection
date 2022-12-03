FPIC_DIR=lib/fpic
LIBS_DIR=lib/shared
SOURCE_FILE_DIR=lib/src

if [ ! -d "$FPIC_DIR" ];
then 
	echo $FPIC_DIR
	echo "Creating /$FPIC_DIR directory"
	mkdir $FPIC_DIR
fi

if [ ! -d "$LIBS_DIR" ];
then
	echo "Creating /$LIBS_DIR directory"
	mkdir $LIBS_DIR
fi

echo "Building shared library"

echo "Building dynamic array libs"
gcc -c -g -fpic -o $FPIC_DIR/dArr.o $SOURCE_FILE_DIR/datastructures/dynamicarray.c
gcc -shared -o $LIBS_DIR/libdArr.so $FPIC_DIR/dArr.o
echo "Build dynamic array uccessfull"

echo "Building error module libs"
gcc -c -g -fpic -o $FPIC_DIR/err.o $SOURCE_FILE_DIR/helper/error.c
gcc -shared -o $LIBS_DIR/liberr.so $FPIC_DIR/err.o
echo "Building error module succesful"

echo "Building stack libs"
gcc -c -g -fpic -o $FPIC_DIR/stack.o $SOURCE_FILE_DIR/datastructures/stack.c -lerr
gcc -shared -o $LIBS_DIR/libstack.so $FPIC_DIR/stack.o $FPIC_DIR/err.o
echo "Building and linking stack successful"

echo "Building image libs"
gcc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/image.o $SOURCE_FILE_DIR/image/image.c -lerr
gcc -shared -o $LIBS_DIR/libimage.so $FPIC_DIR/image.o $FPIC_DIR/err.o
echo "Build and linking image succesful"

echo "Building hashmap"
gcc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/hashmap.o $SOURCE_FILE_DIR/datastructures/hashmap.c -ldArr -lerr 
gcc -shared -o $LIBS_DIR/libhashmap.so $FPIC_DIR/hashmap.o $FPIC_DIR/dArr.o $FPIC_DIR/err.o
echo "Building and linking hashmap succesfull"

echo "Building shape libs"
gcc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/shape.o $SOURCE_FILE_DIR/datastructures/shape.c -lhashmap -ldArr -lerr -lm
gcc -shared -o $LIBS_DIR/libshape.so $FPIC_DIR/shape.o $FPIC_DIR/hashmap.o $FPIC_DIR/dArr.o $FPIC_DIR/err.o -lm
echo "Build and linking shape succesful"

echo "Building bbox"
gcc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/bbox.o $SOURCE_FILE_DIR/image/bbox.c -lhashmap -ldArr -limage -lshape -lerr
gcc -shared -o $LIBS_DIR/libbbox.so $FPIC_DIR/bbox.o $FPIC_DIR/hashmap.o $FPIC_DIR/dArr.o $FPIC_DIR/image.o $FPIC_DIR/shape.o $FPIC_DIR/err.o
echo "Building and linking bbox succesful"

echo "Building thresh"
gcc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/thresh.o $SOURCE_FILE_DIR/image/thresh.c -limage  -lerr
gcc -shared -o $LIBS_DIR/libthresh.so $FPIC_DIR/thresh.o $FPIC_DIR/image.o $FPIC_DIR/err.o 
echo "Building and linking thresh succesful"

echo "building loop_enhancer"
cc -g -c -fpic -Wall -L$LIBS_DIR -Wl,-rpath=$LIBS_DIR -o $FPIC_DIR/enhancer.o $SOURCE_FILE_DIR/image/loop_enhancer.c -limage  -lstack -lerr
gcc -shared -o $LIBS_DIR/libenhancer.so $FPIC_DIR/enhancer.o $FPIC_DIR/image.o $FPIC_DIR/stack.o $FPIC_DIR/err.o 
echo "Building and linking loop enhancer succesful"

if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed"
fi