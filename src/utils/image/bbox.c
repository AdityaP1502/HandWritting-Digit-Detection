#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "../../header/dynamicarray.h"
#include "../../header/hashmap.h"
#include "../../header/shape.h"
#include "../../header/error.h"
#include "../../header/bbox.h"
#include "../../header/image.h"

void* storeInteger(int x) {
   // BE SURE TO FREE THIS POINTER
  int* integer_ptr = malloc(sizeof(int));
  memcpy(integer_ptr, &x, sizeof(int));

  return (void*) integer_ptr;
}

int max(int a, int b) {
  // if a - b >= 0 then a - b >> 31 = 0, therefore yield a
  // if a - b << 0 then a - b >> 31 = -1, therefore yield b
  return a - ((a - b) & (a - b) >> (sizeof(a) * 8 - 1));
}

int min(int a, int b) {
  // if a < b, then -a > -b, therefore min(a, b) = max(-a, -b)
  return -1 * max(-a, -b);
}

void bbox_update(POS* src, int length_src, POS* b, int length_b) {
  int new_loc_i1, new_loc_j1, new_loc_i2, new_loc_j2;
  int min_i, min_j, max_i, max_j;
  if (length_src == 1) die("Error: Invaid src length");

  min_i = src[0]->y;
  min_j = src[0]->x;
  max_i = src[1]->y;
  max_j = src[1]->x;

  if (length_b == 1) {
    // if length only one, min == max
    new_loc_i1 = b[0]->y;
    new_loc_j1 = b[0]->x;
    new_loc_i2 = new_loc_i1;
    new_loc_j2 = new_loc_j1;
  } else {
    new_loc_i1 = b[0]->y; // min i
    new_loc_j1 = b[0]->x; // min j
    new_loc_i2 = b[1]->y; // max i
    new_loc_j2 = b[1]->x; // max j
  }

  // update src value
  src[0]->y = min(min_i, new_loc_i1); 
  src[0]->x = min(min_j, new_loc_j1);
  src[1]->y = max(max_i, new_loc_i2);
  src[1]->x = max(max_j, new_loc_j2);
}

POS* bbox_resolve(NODE* roots, int length, updateFnc update) {
  POS* ref = roots[0]->pos;
  for (int i = 1; i < length; i++) {
    update(ref, 2, roots[i]->pos, 2);
  }
  return ref;
}

static void updateObject(BBOX bbox, int member_id, int x, int y) {
  POS new_loc = malloc(sizeof(Position));
  checkmem(new_loc)
  ;
  new_loc->x = x;
  new_loc->y = y;

  NODE node = DynArr_get(bbox->objects, member_id - 1);
  shape_updateValue(node, new_loc, bbox_update);
}

static uint32_t resolvedConflict(BBOX bbox, NODE* roots, int length) {
  return shape_resolveNodeConflict(roots, length, bbox_resolve, bbox_update);
}

static int createObject(BBOX bbox, int x, int y) {
  int id = bbox->objects->end + 2; // assign new id
  POS pos1 = malloc(sizeof (Position));
  checkmem(pos1);
  pos1->x = x;
  pos1->y = y;

  POS pos2 = malloc(sizeof (Position));
  checkmem(pos2);
  pos2->x = x;
  pos2->y = y;
  
  POS* pos_arr = malloc(2 * sizeof (POS));
  checkmem(pos_arr);
  pos_arr[0] = pos1;
  pos_arr[1] = pos2;

  NODE node = shape_init(id, pos_arr);
  DynArr_append(bbox->objects, node); 
  return id;
}

static void searchObjects(BBOX bbox) {
  MAP dict;
  void* key;
  void* value;
  void* default_value = storeInteger(0);
  int* return_value;
  dArr roots; // dynamic array to store all conflicted roots
  int conflict, id, prev_id;
  int n_i = bbox->img_data->ny;
  int n_j = bbox->img_data->nx;
  
  //  upper stram and box consist of member_id of each pixels. Member_id indicate which object this pixels belong to
  //  upper_stream holds data for all pixels on the upper side of current pixel
  //  box holds data for pixel on the left of current pixel
  //  the smallest id is 1, 0 -> no member
  uint32_t* upper_stream = malloc(n_j * sizeof(uint32_t));
  uint32_t box = 0;
  uint8_t* img = bbox->img_data->img;

  for (int i = 0; i < n_i; i++) {
    for (int j = 0; j < n_j; j++) {
      if (image_read_serial(img, n_j, i, j) == 0) {
        if (box != 0) {
          upper_stream[j - 1] = box;
          box = 0;
        }
        continue;
      }
      // because going from upper left to lower right, only need to check pixel from upper and left
      conflict = 0;
      dict = Hashmap_create(NULL, NULL);

      if (box != 0) { 
        Hashmap_set(dict, storeInteger(box), storeInteger(1));
        prev_id = box;
      };

      if (i - 1 >= 0) {
        for (int k = j - 1; k < j + 2; k++) {
          if (k < n_j && image_read_serial(img, n_j, i - 1, k) != 0) {
            id = upper_stream[k];

            key = storeInteger(id);
            value = storeInteger(1);

            return_value = Hashmap_get(dict, key, default_value);
            if (*return_value) continue;
            roots = DynArr_create(4, 1);
            switch (Hashmap_length(dict))
            {
            case 0:
              Hashmap_set(dict, key, value);
              prev_id = id;
              break;
            case 1:
              {
                int id1 = prev_id;
                int id2 = id;
                NODE root1 = shape_getRoot(DynArr_get(bbox->objects, id1 - 1));
                NODE root2 = shape_getRoot(DynArr_get(bbox->objects, id2 - 1));

                if (root1->id != root2->id) {
                  conflict = 1;
                  DynArr_append(roots, root1);
                  DynArr_append(roots, root2);
                  Hashmap_set(dict, key, value);
                }
              }
              break;
            default:
              {
                int isUnique = 1;
                int id3 = id;
                NODE root3 = shape_getRoot(DynArr_get(bbox->objects, id3 - 1));
                for (int i = 0; i < DynArr_length(roots); i++) {
                  // accept root3 if root3 doesn't hve the same id with 
                  // all the element in roots
                  NODE root = DynArr_get(roots, i);
                  if (root3->id == root->id) {
                    // not unique
                    isUnique = 0;
                    break;
                  }
                  if (isUnique) {
                    DynArr_append(roots, root3);
                    Hashmap_set(dict, key, value);
                  }
                }
              }
            }
          }
        }
      }
      int member_id;
      if (Hashmap_length(dict) == 0) {
        // create a new object
        member_id = createObject(bbox, j, i);
      } else {
        if (!conflict) {
          // len(dict) must be 1
          // determine member_id
          member_id = prev_id;
          updateObject(bbox, member_id, j, i);
        } else {
          member_id = resolvedConflict(bbox, (NODE*) roots->arr, roots->end + 1);
        }
      }
      
      // update box and upper stream
      if (!box) {
        box = member_id;
      } else {
        upper_stream[j - 1] = box;
        box = member_id;
      }
      Hashmap_destroy(dict);
    }
  }
}

static BBOX bbox_init(IMAGE img) {
  BBOX new_bbox = malloc(sizeof(BoundingBox));
  checkmem(new_bbox);

  new_bbox->img_data = img;
  new_bbox->objects = DynArr_create(100, 1);
  return new_bbox;
}

static DATA bbox_getObjects(BBOX bbox) {
  dArr arr = DynArr_create(DynArr_length(bbox->objects), 1);
  MAP map = Hashmap_create(NULL, NULL);
  int* returnValue;
  void* key;

  for (int i = 0; i < DynArr_length(bbox->objects); i++) {
    NODE node = DynArr_get(bbox->objects, i);
    NODE root = shape_getRoot(node);
    key = storeInteger(root->id);
    returnValue = Hashmap_get(map, key, storeInteger(0));
    if (!(*returnValue)) {
      DynArr_append(arr, root->pos);
      Hashmap_set(map, key, storeInteger(1));
    } 
  }

  POS** detected_obj = malloc(DynArr_length(arr) * sizeof(POS*));
  checkmem(detected_obj);

  DATA objectData = malloc(sizeof(Data));
  checkmem(objectData);

  for (int i = 0; i < DynArr_length(arr); i++) {
    POS* data = DynArr_get(arr, i); // store position array information (constist of 2 elements)
    POS* newData = malloc(2 * sizeof(POS)); // store two Position object

    // copy data to newData
    for (int j = 0; j < 2; j++) {
      POS position = malloc(sizeof(Position));
      checkmem(position);
      position->x = data[j]->x;
      position->y = data[j]->y;
      newData[j] = position;
    }

    detected_obj[i] = newData;
  }

  // assign data
  objectData->objects = detected_obj;
  objectData->length = DynArr_length(arr);

  // free unused array and hashmap
  Hashmap_destroy(map);
  DynArr_destroy(&arr);

  return objectData;
}

DATA bbox_find(IMAGE img) {
  BBOX bbox = bbox_init(img);
  searchObjects(bbox);
  DATA detected_shapes = bbox_getObjects(bbox);
  // bbox_destroy(bbox);
  return detected_shapes;
}

DATA python_bbox_find(uint8_t* data, int nx, int ny) {
  IMAGE img_data = python_read_image(data, nx, ny);
  return bbox_find(img_data);
}