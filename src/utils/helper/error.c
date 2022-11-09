#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include "../../header/error.h"

void die(const char* message) {
  if (errno) {
      perror(message);
  } else {
      printf("%s\n", message);
  }
  exit(1);
}

void checkmem(void* ptr) {
  if (!ptr) die("Memory Error: Failed Allocate Memory");
}
