./scripts/build.sh
echo "Building Testing Module"
gcc -g -Wall -Lsrc/libs -Wl,-rpath=src/libs src/test/test.c  -lhashmap -lshape -ldArr -lerr -lm