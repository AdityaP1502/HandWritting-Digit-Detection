#include <stdio.h>
#include <stdlib.h>
#include "../../header/error.h"
#include "../../header/stack.h"

STACK stack_init() {
    STACK s = malloc(sizeof(Head));
    s->head = NULL;
    return s;
}

int stack_is_empty(STACK s) {
    if (!s->head) return 1;
    return 0;
}

void stack_push(STACK s, void* data) {
    stackNode* new_node = malloc(sizeof(stackNode));
    new_node->data = data;
    new_node->next = s->head; // assign new head to last head
    
    // chnage new head to head
    s->head = new_node;
}

void stack_destroy(STACK s) {
    while (!stack_is_empty(s)) {
        void* data = stack_pop(s);
        if (data) free(data); // free content in stack
    }
    // free stack
    free(s);
}

void* stack_pop(STACK s) {
    if (stack_is_empty(s)) {
        die("NullPointerError: Trying to pop an empty stack");
    }

    stackNode* pop_head = s->head;

    // change head to next node
    s->head = pop_head->next;

    void* data = pop_head->data;

    // free unused memory for node
    free(pop_head);

    return data;
}