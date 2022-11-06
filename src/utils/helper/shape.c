#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#include "../../header/error.h"
#include "../../header/shape.h"

NODE init(uint32_t id, uint32_t** pos) {
  NODE node = malloc(sizeof(Node));
  node->id = id;
  node->pos = pos;
  node->root = NULL;

  return node;
}

NODE getRoot(NODE node) {
  NODE curr_node = node;
  while (curr_node->root != NULL) {
    curr_node = curr_node -> root;
  }

  return curr_node;
}

uint32_t getID(NODE node) {
  return getRoot(node)->id;
}

int compare(NODE node1, NODE node2) {
  // compare the id of the node
  uint32_t id1 = getID(node1);
  uint32_t id2 = getID(node2);

  if (id1 == id2) return 1;
  return 0;
}

void updateValue(NODE node, uint32_t* new_value, updateFnc update) {
  NODE root = getRoot(node);
  // wrap new_value inside an array
  uint32_t** new_value_new = malloc(sizeof(uint32_t*));
  new_value_new[0] = new_value;
  // update
  update(root, new_value_new);
}

void resolveNodeConflict(NODE* roots, int length, resolveFnc resolve) {
  uint32_t** newRootVal = resolve(roots);
  uint32_t newID = roots[0]->id;

  NODE newRoot = init(newID, newRootVal);

  for (int i = 0; i < length; i++) {
    roots[i]->root = newRoot;
    // remove unused memory
    free(roots[i]->pos);
    roots[i]->pos = NULL;
  }
}
