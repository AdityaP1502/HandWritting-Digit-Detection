#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#include "../../header/error.h"
#include "../../header/shape.h"

NODE shape_init(uint32_t id, POS* pos) {
  NODE node = malloc(sizeof(Node));
  checkmem(node);
  node->id = id;
  node->pos = pos;
  node->root = NULL;

  return node;
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
}

uint32_t shape_resolveNodeConflict(NODE* roots, int length, resolveFnc resolve, updateFnc update) {
  POS* newRootVal = resolve(roots, length, update); // will point to roots[0].pos
  uint32_t newID = roots[0]->id;

  NODE newRoot = shape_init(newID, newRootVal);
  checkmem(newRoot);

  for (int i = 0; i < length; i++) {
    roots[i]->root = newRoot;
    // remove unused memory besides roots[0].pos
    if (i > 0) free(roots[i]->pos); 
    roots[i]->pos = NULL;
  }

  return newID;
}
