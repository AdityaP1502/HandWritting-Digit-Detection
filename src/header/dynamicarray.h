#ifndef dynamicarray
#define dynamicarray

#include <stdlib.h>
#include "error.h"
/*
  Library for dynamic array data structures
*/ 
#define growth_factor 2

typedef void (*readFnc) (void* data);
typedef void (*destroyFnc) (void* data); 

typedef struct dynArr_ {
  void** arr; // store arbitrary data
  int end; // current end of the array
  int max;  // current size of the array
  destroyFnc destroy; // function to remove data stored in the array
} dynArr;

typedef dynArr* dArr;

void DEFAULT_DESTROY(void* data);

void checkBound(dArr dynArr, int index); // check whther index is out of bound
int DynArr_length(dArr dynArr); // return the length of the array

dArr DynArr_create(int initial_max, int empty, destroyFnc destroy); // init a empty dynamic array
void DynArr_destroy(dArr* dynArr_ptr); // destroy all data in a dynamic array

void DynArr_insert(dArr dynArr, void* data, int index); // insert at given index
void DynArr_append(dArr dynArr, void* data); // insert at the back of the array
void DynArr_remove(dArr dynArr, int index); // remove data from given index

void* DynArr_get(dArr dynArr, int index); // get data from dynamic array;
void* DynArr_pop(dArr dynArr); // remove data from the back of the array and return it's value

void DynArr_print(dArr dynArr, readFnc read); // print all element in the array
#endif