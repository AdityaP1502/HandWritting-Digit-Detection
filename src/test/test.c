#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../header/error.h"
#include "../header/dynamicarray.h"
#include "../header/hashmap.h"

void readInteger(void* data) {
  printf("%d ", *((int*) (data)));
}

void* storeInteger(int x) {
   // BE SURE TO FREE THIS POINTER
  int* integer_ptr = malloc(sizeof(int));
  memcpy(integer_ptr, &x, sizeof(int));

  return (void*) integer_ptr;
}

int main() {
  int key_value[6][2] = {
    {1, 2}, {2, 3}, {3, 4}, 
    {5, 6}, {7, 8}, {8, 8}, 
  };

  MAP map = Hashmap_create(NULL, NULL);

  for (int i = 0; i < 6; i++) {
    Hashmap_set(map, storeInteger(key_value[i][0]), storeInteger(key_value[i][1]));
  }

  Hashmap_set(map, storeInteger(key_value[0][0]), storeInteger(-12));
  for (int i = 0; i < 6; i++) {
    void* key = storeInteger(key_value[i][0]);
    int* data = Hashmap_get(map, key, NULL);
    printf("%d\n", *data);
    free(key);
  }

  Hashmap_destroy(map);
  return 0;
}