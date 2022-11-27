#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <string.h>

#include "../../header/error.h"
#include "../../header/shape.h"
#include "../../header/dynamicarray.h"

static void* storeInteger(int x) {
   // BE SURE TO FREE THIS POINTER
  int* integer_ptr = malloc(sizeof(int));
  memcpy(integer_ptr, &x, sizeof(int));

  return (void*) integer_ptr;
}

NODE shape_init(uint32_t id, uint32_t unique_id, POS* pos) {
  NODE node = malloc(sizeof(Node));
  checkmem(node);
  node->id = id;
  node->pos = pos;
  node->root = NULL;
  node->unique_id = unique_id;
  return node;
}

void shape_destroy(dArr nodes) {
  NODE curr_node;
  NODE temp;
  void* key;
  MAP map = Hashmap_create(NULL, NULL, NULL);
  for (int i = 0; i < DynArr_length(nodes); i++) {
    curr_node = DynArr_get(nodes, i);
    while (curr_node) {
      temp = curr_node;
      key = storeInteger(curr_node->unique_id);
      if (!Hashmap_get(map, key, NULL)) {
        Hashmap_set(map, storeInteger(temp->unique_id), temp);
        if (temp->pos)
        {
          free(temp->pos[0]);
          free(temp->pos[1]);
          free(temp->pos);
        }
      }
      free(key);
      curr_node = curr_node->root;
    }
  }
  Hashmap_destroy(map);
}

NODE shape_getRoot(NODE node) {
  NODE curr_node = node;
  while (curr_node->root != NULL) {
    curr_node = curr_node -> root;
  }

  return curr_node;
}

uint32_t shape_getID(NODE node) {
  return shape_getRoot(node)->id;
}

int shape_compare(NODE node1, NODE node2) {
  // compare the id of the node
  uint32_t id1 = shape_getID(node1);
  uint32_t id2 = shape_getID(node2);

  if (id1 == id2) return 1;
  return 0;
}

void shape_updateValue(NODE node, POS new_value, updateFnc update) {
  NODE root = shape_getRoot(node);
  // wrap new_value inside an array
  POS* new_value_new = malloc(sizeof(POS));
  new_value_new[0] = new_value;
  // update
  update(root->pos, 2, new_value_new, 1);
  free(new_value_new);
}

uint32_t shape_resolveNodeConflict(NODE* roots, int length, uint32_t unique_id, resolveFnc resolve, updateFnc update) {
  POS* newRootVal = resolve(roots, length, update); // will point to roots[0].pos
  uint32_t newID = roots[0]->id;

  NODE newRoot = shape_init(newID, unique_id, newRootVal);
  checkmem(newRoot);

  for (int i = 0; i < length; i++) {
    roots[i]->root = newRoot;
    // remove unused memory besides roots[0].pos
    if (i > 0) {
      free(roots[i]->pos[0]);
      free(roots[i]->pos[1]);
      free(roots[i]->pos); 
    }

    roots[i]->pos = NULL;
  }

  // there are length node connected to new root
  

  return newID;
}
