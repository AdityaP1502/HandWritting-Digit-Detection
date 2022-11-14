#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "../../header/error.h"
#include "../../header/dynamicarray.h"
#include "../../header/hashmap.h"
#include "../../header/shape.h"
#include "../../header/image.h"
#include "../../header/bbox.h"
#include "../../header/sort.h"

static void* storeInteger(int x) {
   // BE SURE TO FREE THIS POINTER
  int* integer_ptr = malloc(sizeof(int));
  memcpy(integer_ptr, &x, sizeof(int));

  return (void*) integer_ptr;
}

static int max(int a, int b) {
  // if a - b >= 0 then a - b >> 31 = 0, therefore yield a
  // if a - b << 0 then a - b >> 31 = -1, therefore yield b
  return a - ((a - b) & (a - b) >> (sizeof(a) * 8 - 1));
}

static int min(int a, int b) {
  // if a < b, then -a > -b, therefore min(a, b) = max(-a, -b)
  return -1 * max(-a, -b);
}

static void bbox_update(POS* src, int length_src, POS* b, int length_b) {
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

static POS* bbox_resolve(NODE* roots, int length, updateFnc update) {
  POS* ref = roots[0]->pos;
  for (int i = 1; i < length; i++) {
    update(ref, 2, roots[i]->pos, 2);
  }
  return ref;
}

static void updateObject(BBOX bBox, int member_id, int x, int y) {
  POS new_loc = malloc(sizeof(Position));
  checkmem(new_loc)
  ;
  new_loc->x = x;
  new_loc->y = y;

  NODE node = DynArr_get(bBox->objects, member_id - 1);
  shape_updateValue(node, new_loc, bbox_update);
}

static uint32_t resolvedConflict(BBOX bBox, NODE* roots, int length) {
  return shape_resolveNodeConflict(roots, length, bbox_resolve, bbox_update);
}

static int createObject(BBOX bBox, int x, int y) {
  int id = bBox->objects->end + 2; // assign new id
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
  DynArr_append(bBox->objects, node); 
  return id;
}

static void searchObjects(BBOX bBox) {
  MAP dict;
  void* key;
  void* value;
  void* default_value = storeInteger(0);
  int* return_value;
  dArr roots; // dynamic array to store all conflicted roots
  int conflict, id, prev_id;
  int n_i = bBox->img_data->ny;
  int n_j = bBox->img_data->nx;
  
  //  upper stram and box consist of member_id of each pixels. Member_id indicate which object this pixels belong to
  //  upper_stream holds data for all pixels on the upper side of current pixel
  //  box holds data for pixel on the left of current pixel
  //  the smallest id is 1, 0 -> no member
  uint32_t* upper_stream = calloc(n_j, sizeof(uint32_t));
  uint32_t box = 0;
  uint8_t* img = bBox->img_data->img;

  for (int i = 0; i < n_i; i++) {
    for (int j = 0; j < n_j; j++) {
      if (image_read_serial(img, n_j, i, j) == BG_PIXELS_INTENSITY) {
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
          if (k >= 0 && k < n_j && image_read_serial(img, n_j, i - 1, k) != BG_PIXELS_INTENSITY) {
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
                NODE root1 = shape_getRoot(DynArr_get(bBox->objects, id1 - 1));
                NODE root2 = shape_getRoot(DynArr_get(bBox->objects, id2 - 1));

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
                NODE root3 = shape_getRoot(DynArr_get(bBox->objects, id3 - 1));
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
        member_id = createObject(bBox, j, i);
      } else {
        if (!conflict) {
          // len(dict) must be 1
          // determine member_id
          member_id = prev_id;
          updateObject(bBox, member_id, j, i);
        } else {
          member_id = resolvedConflict(bBox, (NODE*) roots->arr, roots->end + 1);
        }
      }
      
      // update box and upper stream
      if (!box) {
        box = member_id;
      } else {
        upper_stream[j - 1] = box;
        box = member_id;
      }

      // edge cases
      if (j == n_j - 1) {
        upper_stream[j] = box;
        box = 0;
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

static DATA bbox_getObjects(BBOX bBox) {
  dArr arr = DynArr_create(DynArr_length(bBox->objects), 1);
  MAP map = Hashmap_create(NULL, NULL);
  int* returnValue;
  void* key;

  for (int i = 0; i < DynArr_length(bBox->objects); i++) {
    NODE node = DynArr_get(bBox->objects, i);
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

static int compare_min_i(void* a, void* b) {
  // return true if a.min_i < b.min_i
  POS* vertex_a = a;
  POS* vertex_b = b;

  return vertex_a[0]->y < vertex_b[0]->y;
}

static int compare_min_j(void* a, void* b) {
  // return true if a.min_i < b.min_i
  POS* vertex_a = a;
  POS* vertex_b = b;

  return vertex_a[0]->x < vertex_b[0]->x;
}

static dArr getPartition(DATA objs) {
  // based on implementation 
  // objs is sorted based on min_i value
  // so not require additional sort

  uint32_t hi;
  dArr partitons = DynArr_create(1, 1);
  hi = objs->objects[0][1]->y;

  for (int i = 1; i < objs->length; i++) {
    // check if current object fit into frames
    if (objs->objects[i][0]->y <= hi) {
      if (objs->objects[i][1]->y > hi) {
        // object fit into frame, and the the max_i exceed current frame
        // update frame 
        hi = objs->objects[i][1]->y;
      }
      continue;
    }
    // object not inside the frames
    DynArr_append(partitons, storeInteger(i - 1));
    // init new frames
    hi = objs->objects[i][1]->y;
  }
  // edge cases
  DynArr_append(partitons, storeInteger(objs->length - 1));
  return partitons;
}

dArr sortObjs(DATA objs) {
  // printf("%d\n", objs->length);
  // dArr partitions = DynArr_create(1, 1);
  // // sorted objects
  // printf("%p\n", objs);
  // printf(objs->length);
  // printf("%p\n", objs->objects);

  int partition_length, end;
  POS** curr_partition;

  dArr partitions = getPartition(objs);
  int offset = 0;
  int start = 0;
  for (int i = 0; i < DynArr_length(partitions); i++) {
    end = *((int*)(DynArr_get(partitions, i)));
    partition_length = (end - start) + 1;
    curr_partition = objs->objects + start;
    array_sort((void**)curr_partition, partition_length, compare_min_j);
    start = end + 1;
  }

  return partitions;
}

DATA bbox_find(IMAGE img) {
  BBOX bBox = bbox_init(img);
  searchObjects(bBox);
  DATA detected_shapes = bbox_getObjects(bBox);
  printf("%p\n", detected_shapes);
  // bbox_destroy(bBox);
  return detected_shapes;
}

DATA python_bbox_find(void* data, int nx, int ny) {
  IMAGE img_data = python_read_image(data, nx, ny);
  DATA objs = bbox_find(img_data);
  // sortObjs(objs);
  return objs;
}

static void filterImages(uint8_t* img, int nx, POS* frames, POS* filteredRegion) {
  int min_i, min_j, max_i, max_j;

  min_j = max(frames[0]->x, filteredRegion[0]->x);
  min_i = max(frames[0]->y, filteredRegion[0]->y);
  max_i = min(frames[1]->y, filteredRegion[1]->y);
  max_j = min(frames[1]->x, filteredRegion[1]->x);
  // Change any set pixels in filteredRegion back to BG INTENSITY
  for (int i = min_i; i < max_i + 1; i++) {
    for (int j = min_j; j < max_j + 1; j++) {
      image_write_serial(img, nx, i - frames[0]->y, j - frames[0]->x, BG_PIXELS_INTENSITY);
    }
  }
}

IMAGE get_shapes(IMAGE img, DATA objs, int partition_start, int partition_end, int idx) {
  // return detected shapes
  POS* obj; 
  int ny, nx, lo, hi;
  uint8_t* object_image_copy;

  obj = objs->objects[idx];
  printf("%d,%d,%d,%d\n", obj[0]->y, obj[0]->x, obj[1]->y, obj[1]->x);

  // image dimensions
  nx = (obj[1]->x - obj[0]->x) + 1; 
  ny = (obj[1]->y - obj[0]->y) + 1;

  // start location
  object_image_copy = malloc((nx * ny) * sizeof(uint8_t));

  // copy to new frames
  // for (int i = 0; i < ny; i++) {
  //   memcpy(object_image_copy + offset_copy, object_image + offset, nx * sizeof(uint8_t));
  //   offset += img->nx;
  //   offset_copy += nx;
  // }
  uint8_t t_;
  for (int i = 0; i < ny; i++) {
    for (int j = 0; j < nx; j++) {
      t_ = image_read_serial(img->img, img->nx, obj[0]->y + i, obj[0]->x + j);
      image_write_serial(object_image_copy, nx, i, j, t_);
    }
  }
  // Filter shapes to remove any images that overlap with the frames

  // do removal for element with min j less than current frames
  lo = idx - 1;
  while (lo >= partition_start && objs->objects[lo][1]->x > obj[0]->x) {
    filterImages(object_image_copy, nx, obj, objs->objects[lo]);
    lo--;
  }

  // do removal for element with min j greater than current frames
  hi = idx + 1;
  while (hi <= partition_end && objs->objects[hi][0]->x < obj[1]->x) {
    filterImages(object_image_copy, nx, obj, objs->objects[hi]);
    hi++;
  }

  // Create new image objects
  IMAGE obj_img = malloc(sizeof(Image));
  obj_img->img = object_image_copy;
  obj_img->nx = nx;
  obj_img->ny = ny;

  return obj_img;
}
