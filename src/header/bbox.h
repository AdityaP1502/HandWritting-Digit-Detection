#include <stdlib.h>
#include <stdint.h>
#include "dynamicarray.h"
#include "hashmap.h"
#include "shape.h"
#include "error.h"

typedef struct Image_ {
  uint8_t** image;
  int nx; 
  int ny;
} Image;
typedef Image* IMAGE;

typedef struct BoundingBox_ {
  IMAGE img; // pixels
  dArr objects; // array of node
  uint8_t** result; // image bbox result
} BoundingBox;

typedef struct Data_ {
  POS** objects;
  int length;
} Data;

typedef BoundingBox* BBOX;
typedef Data* DATA;

int max(int a, int b);
int min(int a, int b);

void bbox_update(POS* src, int length_src, POS* b, int length_b);
POS* bbox_resolve(NODE* roots, int length, updateFnc update);

// Find all object in image
DATA bbox_find(IMAGE image);

DATA python_bbox_find(uint8_t* data, int nx, int ny);
