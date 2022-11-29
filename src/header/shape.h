#ifndef shape
#define shape

#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include "dynamicarray.h"
#include "hashmap.h"
#include "error.h"

/* 
Shape datastructures that are used in bbox algorithm
*/
typedef struct Position_ {
  uint32_t x;
  uint32_t y;
} Position;

typedef Position* POS;

typedef struct Node_ {
  struct Node_* root;
  uint32_t id;
  POS* pos;
  uint32_t unique_id;
} Node;



typedef Node* NODE;

// update value function 
typedef void (*updateFnc) (POS* src, int length_src, POS* new_value, int length_new_value);
typedef POS* (*resolveFnc) (NODE* roots, int length, updateFnc update);

// create a node
NODE shape_init(uint32_t id, uint32_t unique_id, POS* pos); 
// destroy shape
void shape_destroy(dArr nodes);

NODE shape_getRoot(NODE node); // get root from a given node
uint32_t shape_getID(NODE node); // get root id of a given node

int shape_compare(NODE node1, NODE node2); // compare two root id

void shape_updateValue(NODE node, POS new_value, updateFnc update); // update root value using given update function
uint32_t shape_resolveNodeConflict(NODE* roots, int length, uint32_t unique_id, resolveFnc resolve, updateFnc update); // resolve conflict that occurs

#endif