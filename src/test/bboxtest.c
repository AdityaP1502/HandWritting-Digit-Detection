#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../header/error.h"
#include "../header/dynamicarray.h"
#include "../header/hashmap.h"
// #include "../header/bbox.h"
#include "../header/loop_counter.h"
#include "../header/image.h"

#define MAX_FILESIZE 4096
#define MAX_LINE 50

void readFile (char* dst, char* filename) {
  FILE* file = fopen(filename, "r+");
  checkmem(file);

  int rc = fread(dst, sizeof(char), MAX_FILESIZE, file);
  if (rc > MAX_FILESIZE) die("Failed to load file");
}

int readLines(char** line, char* filename) {
  char* contents = malloc(MAX_FILESIZE * sizeof(char));
  readFile(contents, filename);
  int start = 0;
  int lineCount = 0;
  for (int i = 0; i < MAX_FILESIZE; i++) {
    if (contents[i] == '\0') break;
    if (contents[i] == '\n') {
      int length = (i - start); // don't include the \n character
      char* lineContent = malloc((length + 2) * sizeof(char));
      memcpy(lineContent, contents + start, length);
      lineContent[length] = ',';
      line[lineCount] = lineContent;

      start = i  + 1; // move the offset
      lineCount++; // update the line count
    }
  }
  return lineCount;
}

uint8_t convertTextToBytes(char* src, int length) {
  char* num_string = malloc((length + 1) * sizeof(char));
  memcpy(num_string, src, length);
  int string_int = atoi(num_string);
  if (string_int > 255) die("Invalid bytes. Pixel value can't exceed 255");
  return (uint8_t) string_int;
}

int readPixels(uint8_t* pixel_line, char* line, int length) {
  int start = 0;
  int ctr = 0;
  for (int i = 0; i < length; i++) {
    if (line[i] == ',') {
      int length = i - start;
      pixel_line[ctr] = convertTextToBytes(line + start, length);
      ctr++;
    }
    if (line[i] == ' ') start = i + 1;
  }
  return ctr;
}

IMAGE readImage(char* filename) {
  char** lines = malloc(MAX_LINE * sizeof(char*));
  int cnt = readLines(lines, filename);
  int ctr = 0;
  uint8_t** pixels = malloc(cnt * sizeof(uint8_t*));
  for (int i = 0; i < cnt; i++) {
    uint8_t* pixel_line = malloc(strlen(lines[i]) * sizeof(uint8_t));
    ctr = readPixels(pixel_line, lines[i], strlen(lines[i]));
    pixels[i] = pixel_line;
  }

  IMAGE img = malloc(sizeof(Image));
  img->img = image_to_serial(pixels, ctr, cnt);
  img->nx = ctr;
  img->ny = cnt;

  return img;
}

int main() {
  char filename[] = "/home/adityap/Documents/Pemlan/HandWritting-Digit-Detection/src/test/testData/4.txt";
  IMAGE img = readImage(filename);
  printf("nx: %d, ny: %d\n", img->nx, img->ny);

  for (int i = 0; i < img->ny; i++) {
    for (int j = 0; j < img->nx; j++) {
      printf("%d ", image_read_serial(img->img, img->nx, i, j));
    }
    printf("\n");
  }

  // bbox_find(img);
  loopCounter* counter = loop_counter_init(img);
  printf("%d\n", loop_count(counter));
}