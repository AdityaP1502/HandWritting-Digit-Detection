#ifndef error
#define error

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

/*
  Library for sending error message
*/

void die(const char* message);

void checkmem(void* ptr);

#endif