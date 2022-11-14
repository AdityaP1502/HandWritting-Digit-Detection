#ifndef loop_counter
#define loop_counter

#include <stdlib.h>
#include <stdio.h>
#include "error.h"
#include "image.h"
#include "stack.h"


/* DEFINE DATASTRUCTURES */
typedef struct Position_ {
    int i; 
    int j;
} Position;

typedef Position* POS; 

// typedef struct Vertex_ {
//     POS key;
//     dArr conn;
// };


// Function to update current position
typedef void (*updatePos) (POS pos);

typedef struct loop_counter_ {
    IMAGE img;
    updatePos* update_fnc;
    POS* end_pos;
    STACK s;
    uint8_t* dp;
} loopCounter;


// init loop counter
loopCounter* loop_counter_init(IMAGE img);

// // Check if pos a boudnary
// int isBoundary(loopCounter* counter, POS pos);

// // get direction to boundary pixels from pos
// int* getNeightborBoundary(loopCounter* counter, POS pos);

// // tranverse all node connected to start vertex
// void tranverse(loopCounter* counter;

// count loop in images
int loop_count(loopCounter* counter);

// python interface
int python_loop_count(uint8_t* img, int nx, int ny);
#endif