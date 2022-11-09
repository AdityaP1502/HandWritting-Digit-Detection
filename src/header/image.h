#ifndef image
#define image

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "error.h"


typedef struct Image_ {
  uint8_t* img;
  int nx; 
  int ny;
} Image;
typedef Image* IMAGE;

// Read Image Data sent from python. Image is a serial of bits instead of matrix
IMAGE python_read_image(uint8_t* data, int nx, int ny);

// read serial image using matrix row and colm pos (i and j)
uint8_t image_read_serial(uint8_t* img, int nx, int i, int j);

// Change image in matrix form to serial form
uint8_t* image_to_serial(uint8_t** img, int nx, int ny);
#endif