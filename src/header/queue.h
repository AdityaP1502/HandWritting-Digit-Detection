#ifndef queue
#define queue

#include <stdio.h>
#include <stdlib.h>
#include "error.h"

typedef struct queueNode_ {
  void* data;
  struct Node_* next;
} queueNode;

typedef struct queue_ {
  queueNode* head;
  queueNode* tail;
} Queue;

typedef Queue* QUEUE;

// Initialize queue
QUEUE queue_init();

// push element into a queue
void queue_push(QUEUE queue, void* data);

// pop element from a queue and return the data
void* queue_pop(QUEUE queue);

// check if queue is empty
int queue_is_empty(QUEUE queue);







#endif