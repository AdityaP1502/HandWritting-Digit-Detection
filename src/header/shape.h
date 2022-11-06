#ifndef shape
#define shape

#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include "error.h"

/* 
Shape datastructures that are used in bbox algorithm
*/

typedef struct Node_ {
  struct Node_* root;
  uint32_t id;
  uint32_t** pos;
} Node;

typedef Node* NODE;

// update value function 
typedef void (*updateFnc) (NODE node, uint32_t** new_value);
typedef uint32_t** (*resolveFnc) (NODE* roots);

NODE init(uint32_t id, uint32_t** pos); // create a node

NODE getRoot(NODE node); // get root from a given node
uint32_t getID(NODE node); // get root id of a given node

int compare(NODE node1, NODE node2); // compare two root id

void updateValue(NODE node, uint32_t* new_value, updateFnc update); // update root value using given update function
void resolveNodeConflict(NODE* roots, int length, resolveFnc resolve); // resolve conflict that occurs

#endif