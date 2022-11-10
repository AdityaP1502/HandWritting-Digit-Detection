#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../../header/error.h"
#include "../../header/image.h"

IMAGE python_read_image(uint8_t* data, int nx, int ny) {
  size_t size = nx * ny * sizeof(uint8_t);
  uint8_t* img = malloc(size);
  checkmem(img);

  // copy data to img
  memcpy(img, data, size);

  // // printf("%d\n", data[300]);
  // uint8_t* arr = malloc(nx * sizeof(uint8_t));

  // for (int n = 0; n < ny * nx; n++) {
  //   arr[j] = data[n];
  //   j++;
  //   if (j == nx) {
  //     img[i] = arr;
  //     j = 0;
  //     i++;
  //     arr = malloc(nx * sizeof(uint8_t));
  //   }
  // }

  IMAGE img_data = malloc(sizeof(Image));
  checkmem(img_data);
  img_data->img = img;
  img_data->nx = nx;
  img_data->ny = ny;

  return img_data;
}

uint8_t image_read_serial(uint8_t* data, int nx, int i, int j) {
  int n = i * nx + j;
  return data[n];
}

uint8_t* image_to_serial(uint8_t** img, int nx, int ny) {
  int n;
  uint8_t* img_serial = malloc(nx * ny*sizeof(uint8_t));
  for (int i = 0; i < ny; i++) {
    for (int j = 0; j < nx; j++) {
      n = nx * i + j;
      img_serial[n] = img[i][j];
    }
  }
  return img_serial;
}