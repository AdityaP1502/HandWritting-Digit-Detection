#include <stdlib.h>
#include <stdint.h>
#include "dynamicarray.h"
#include "hashmap.h"
#include "queue.h"
#include "shape.h"
#include "error.h"
#include "image.h"

typedef struct BoundingBox_ {
  IMAGE img_data; // pixels
  dArr objects; // array of node
} BoundingBox;

typedef struct BoundingBoxOptimized_ {
  IMAGE_OPT img_data; // pixels
  dArr objects; // array of node
} BoundingBoxOptimized;

typedef struct Data_ {
  POS** objects;
  int length;
} Data;

typedef BoundingBox* BBOX;
typedef BoundingBoxOptimized* BBOX_OPT;
typedef Data* DATA;

// int max(int a, int b);
// int min(int a, int b);

// void bbox_update(POS* src, int length_src, POS* b, int length_b);
// POS* bbox_resolve(NODE* roots, int length, updateFnc update);

// Find all object in image
DATA bbox_find(IMAGE image);

DATA python_bbox_find(void* data, int nx, int ny);

