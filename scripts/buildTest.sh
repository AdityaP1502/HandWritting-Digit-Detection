./scripts/build.sh
echo "Building Testing Module"
gcc -g -Wall -Lsrc/libs -Wl,-rpath=src/libs src/test/bboxtest.c  -lbbox -lhashmap -lshape -ldArr -lerr -lm