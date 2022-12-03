#ifndef hashmap
#define hashmap

#include <stdlib.h>
#include <stdint.h>

#include "error.h"
#include "dynamicarray.h"
#include "error.h"

/*
  Library for hashmap datastructures
*/
#define DEFAULT_NUMBER_OF_BUCKETS 100

typedef int (*Hashmap_compare) (void* a, void* b);
typedef uint32_t (*Hashmap_hash) (void* key);

typedef struct Hashmap_ {
  dArr buckets;
  Hashmap_compare cmp;
  Hashmap_hash hash;
  destroyFnc destroy;
  int length;
} Hashmap;

typedef Hashmap* MAP;

typedef struct Hashmap_node {
  void* key;
  void* data;
  uint32_t hash;
} HashmapNode;

typedef int (*Hashmap_tranverse_cb) (HashmapNode* node);

MAP Hashmap_create(Hashmap_compare cmp, Hashmap_hash hash, destroyFnc destroy); // create a new hashmap
void Hashmap_destroy(MAP Hashmap); // destroy all hashmap content

void Hashmap_set(MAP map, void* key, void* data); // insert data into the hashmap
void* Hashmap_get(MAP map, void* key, void* default_value); // get value from the hashmap

// int Hashmap_tranverse(MAP map, Hashmap_tranverse_cb tranverse_cb); // tranverse the hasmap if found conflict
void* Hashmap_delete(MAP map, void* key); // delete a key from hashmap

int Hashmap_length(MAP map); // return the length of the map
#endif