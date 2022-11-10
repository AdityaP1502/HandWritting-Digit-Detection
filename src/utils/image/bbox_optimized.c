#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "../../header/error.h"
#include "../../header/dynamicarray.h"
#include "../../header/queue.h"
#include "../../header/hashmap.h"
#include "../../header/shape.h"
#include "../../header/image.h"
#include "../../header/bbox.h"

static BBOX tranverse(BBOX_OPT bbox, int i, int j, int id) {
  // all pixel that come from here  
  // tranverse node
  uint32_t t;
  POS pos, curr_pos;
  int last_i, last_j;

  pos = malloc(sizeof(Position));
  pos->x = j;
  pos->y = i;

  QUEUE st = queue_init();
  queue_push(st, pos);
  uint32_t* to_img = bbox->img_data->img;
  while (!queue_is_empty(st)) {
    curr_pos = queue_pop(st);
    // check if 
  }
}

static BBOX searchObjects_2(BBOX bbox) {
  // a much faster approach
  // has runtime complexity of O(MN) with space complexity O(N_OBJECTS)
}

DATA bbox_find(IMAGE img) {
  BBOX bbox = bbox_init(img);
  searchObjects(bbox);
  DATA detected_shapes = bbox_getObjects(bbox);
  // bbox_destroy(bbox);
  return detected_shapes;
}

DATA python_bbox_find(void* data, int nx, int ny) {
  IMAGE img_data = python_read_image_optimized(data, nx, ny);
  return bbox_find(img_data);
}