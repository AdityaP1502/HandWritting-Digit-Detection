#ifndef loop_counter
#define loop_counter

#include <stdlib.h>
#include <stdio.h>
#include "error.h"
#include "image.h"
#include "stack.h"


/* DEFINE DATASTRUCTURES */

typedef struct Data_
{
    int i;
    int j_start;
    int j_end;
} Data;

typedef Data *DATA;

// typedef struct Vertex_ {
//     POS key;
//     dArr conn;
// };


// Function to update current position
typedef int (*update_fnc) (int j);

// comparison fucntion
typedef int (*condition_fnc) (uint8_t val);

typedef struct loop_counter_ {
    IMAGE img;
    STACK s;
    uint8_t* dp;
} loopCounter;


// init loop counter
loopCounter* loop_counter_init(IMAGE img);

// count loop in images
int loop_count(loopCounter* counter);

// python interface
int python_loop_count(uint8_t* img, int nx, int ny);
#endif