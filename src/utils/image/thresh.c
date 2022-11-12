#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "../../header/image.h"
#include "../../header/error.h"
#include "../../header/thresh.h"

IMAGE python_thresh_images(uint8_t* img, int nx, int ny, uint8_t min_thresh, uint8_t max_thresh) {
  int n = nx * ny;
  
  for (int i = 0; i < n; i++) {
    if (img[i] >= min_thresh && img[i] <= max_thresh) {
      img[i] = DATA_PIXELS_INTENSITY;
    } else {
      img[i] = BG_PIXELS_INTENSITY;
    }
  }

  IMAGE img_data = malloc(sizeof(IMAGE));

  img_data->img = img;
  img_data->nx = nx;
  img_data->ny = ny;

  return img_data;
}