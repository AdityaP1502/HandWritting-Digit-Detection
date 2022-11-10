#include <stdio.h>
#include <stdlib.h>
#include "../../header/queue.h"

QUEUE queue_init() {
  QUEUE new_stack = malloc(sizeof(Queue));
  new_stack->head = NULL;
  new_stack->tail = NULL;
  return new_stack;
}

int queue_is_empty(QUEUE st) {
  return !st->head;
}

void queue_push(QUEUE st, void* data) {
  // create a new node and store data location in new node
  queueNode* new_node = malloc(sizeof(queueNode));
  new_node->data = data;

  if (queue_is_empty(st)) {
    // if empty, initialize node
    // head and tail point to the same node
    st->head = new_node;
    st->tail = new_node;
    return;
  }

  // new_data need to be placed in the end
  st->tail.next = new_node; // link last tail to new node

  // change queue tail
  st->tail = new_node;
}

void* queue_pop(QUEUE st) {
  void* to_data = st->head->data;
  queueNode* pop_head = st->head;

  st->head = st->head->next;
  if (st->head == NULL) {
    // create an empty queue
    st->tail = NULL;
  }

  free(pop_head);
  return to_data;
}


