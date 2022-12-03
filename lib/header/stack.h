#ifndef stack
#define stack

#include <stdio.h>
#include <stdlib.h>
#include "error.h"

typedef struct stackNode_ {
    void* data;
    struct stackNode_* next;
} stackNode;

typedef struct stackHead_ {
    stackNode* head;
} Head;

typedef Head* STACK;

// create new stack
STACK stack_init();

// check whether stack is empty
int stack_is_empty(STACK s);

// insert data to stack
void stack_push(STACK s, void* data);

// destroy all element in stack
void stack_destroy(STACK s);

// pop data from stack
void* stack_pop(STACK s);

// peek the top eleemnt from stack
void* stack_peek(STACK s);

#endif