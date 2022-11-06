#include <stdlib.h>
#include "../../header/dynamicarray.h"

void checkBound(dArr dynArr, int index) {
  if (dynArr->end < index) {
    char* errMessage = malloc(sizeof(char) * 150);
    errMessage[149] = '\0'; // null bytes
    sprintf(errMessage, "IndexOutOfBoundError: Trying to access index %d from array with size %d", index, dynArr->end);
    die(errMessage);
  }
}

int DynArr_length(dArr dynArr) {
  return dynArr->end + 1;
}

dArr DynArr_create(int initial_max, int empty) {
  if (!initial_max) die("Error: Initial max must have value greater than 0");

  dArr new_array = malloc(sizeof(dynArr));
  checkmem(new_array);

  if (empty) {
    new_array->arr = malloc(initial_max * sizeof *new_array->arr);
    new_array->end = -1;

  } else {
    new_array->arr = calloc(initial_max, sizeof *new_array->arr);
    new_array->end = initial_max - 1;
  }
  
  new_array->max = initial_max;

  return new_array;
}

void DynArr_destroy(dArr* dynArr_ptr) {
  dArr dynArr = *dynArr_ptr;
  if (dynArr) {
    // free all the contents
    for (int i = 0; i < DynArr_length(dynArr); i++) {
      void* data = DynArr_get(dynArr, i);
      if (data) {
        free(data);
      }
    }

    // free the array
    free(dynArr->arr);
    free(dynArr);
    
    // set pointer to the array to NULL
    *dynArr_ptr = NULL;
  }
}

void DynArr_insert(dArr dynArr, void* data, int index) {
  checkBound(dynArr, index);
  // overwrite data with new data
  void* overwritten_data = dynArr->arr[index];
  free(overwritten_data); // delete overwritten data

  dynArr->arr[index] = data;
}

void DynArr_expand(dArr dynArr) {
  // expand the array then copy all the content into the new array
  dynArr->max *= growth_factor;
  size_t new_size = dynArr->max * sizeof(void*);

  void** new_arr = malloc(new_size);
  checkmem(new_arr);

  for(int i = 0; i < DynArr_length(dynArr); i++) {
    new_arr[i] = dynArr->arr[i];
  }

  void** prev_arr = dynArr->arr;
  dynArr->arr = new_arr;

  free(prev_arr);
}

void DynArr_append(dArr dynArr, void* data) {
  // check if there enough space to fit new data at the end
  if (dynArr->end == (dynArr->max) - 1) DynArr_expand(dynArr);

  // Append item
  dynArr->arr[(dynArr->end) + 1] = data;
  dynArr->end++; // update the end
}

void DynArr_remove(dArr dynArr, int index) {
  checkBound(dynArr, index);
  // free removed element
  void* removed_element = dynArr->arr[index];
  free(removed_element);

  // move all element on the right side of index to the left
  for (int i = index; i < dynArr->end; i++) {
    dynArr->arr[i] = dynArr->arr[i + 1];
  }

  dynArr->end--; // remove end
}

void* DynArr_get(dArr dynArr, int index) {
  checkBound(dynArr, index);
  return dynArr->arr[index];
}

void* DynArr_pop(dArr dynArr) {
  int prev_end = dynArr->end;
  dynArr->end--;
  return dynArr->arr[prev_end];
}

void DynArr_print(dArr dynArr, readFnc read) {
  for (int i = 0; i < DynArr_length(dynArr); i++) {
    read(DynArr_get(dynArr, i));
  }
  printf("\n");
}