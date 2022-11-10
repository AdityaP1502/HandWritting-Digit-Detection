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

typedef struct ImageOptimized_ {
  uint32_t* img;
  int nx;
  int ny;
} ImageOptimized;

typedef Image* IMAGE;
typedef ImageOptimized* IMAGE_OPT;

// Read Image Data sent from python. Image is a serial of bits instead of matrix
IMAGE python_read_image(uint8_t* data, int nx, int ny);

// read image Data sent from python when optimized flag set to 1
IMAGE_OPT python_read_image_optimized(uint32_t* data, int nx, int ny);

// read serial image using matrix row and colm pos (i and j)
uint8_t image_read_serial(uint8_t* img, int nx, int i, int j);

// write serial image using matrix row and colm pos (i and j)
void image_write_serial(uint8_t* img, int nx, int i, int j, uint8_t new_pixel_value);

// read serial image using matrix row and colm pos (i and j).For Optimized Version
uint32_t image_read_serial_optimized(uint32_t* img, int nx, int i, int j);

// write serial image using matrix row and colm pos (i and j).For Optimized Version
void image_write_serial_optimized(uint32_t* img, int nx, int i, int j, uint32_t new_pixel_value);

// Change image in matrix form to serial form
uint8_t* image_to_serial(uint8_t** img, int nx, int ny);
#endif