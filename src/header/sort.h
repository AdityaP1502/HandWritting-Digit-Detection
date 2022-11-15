#ifndef sort
#define sort

#include <stdio.h>
#include "error.h"

// compare function
// return True if a < b
typedef int (*compareFnc) (void* a, void* b);

// sort array
void array_sort(void** arr, int n, compareFnc cmp);

#endif
