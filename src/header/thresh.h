#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "image.h"
#include "error.h"

// thresh_images -> if pixel between thresh value, will be converted to 0, else will be converted to 255
IMAGE python_thresh_images (uint8_t* img, int nx, int ny, uint8_t min_thresh, uint8_t max_thresh);