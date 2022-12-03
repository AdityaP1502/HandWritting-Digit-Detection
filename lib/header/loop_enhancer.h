#ifndef loop_counter
#define loop_counter

#include <stdlib.h>
#include <stdio.h>
#include "error.h"
#include "image.h"
#include "stack.h"



#define DATA_PIXEL_INTENSITY 127
#define DATA_LOOP_PIXEL_INTENSITY_FIRST 191
#define DATA_LOOP_PIXEL_INTENSITY_LAST 255
#define MAXIMUM_COUNT 2
#define BG_PIXELS_UPPER 5

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

typedef struct loop_enhancer_ {
    IMAGE img;
    STACK s;
    uint8_t* dp;
} loopEnhnacer;


// init loop counter
loopEnhnacer* loop_enhancer_init(IMAGE img);

// count loop in images
void loop_enhance(loopEnhnacer* counter);

// python interface
void python_loop_enhance(uint8_t* img, int nx, int ny);
#endif