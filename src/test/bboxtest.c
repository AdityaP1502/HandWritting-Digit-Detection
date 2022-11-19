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
  uint8_t arr[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,51,159,253,159,50,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,48,238,252,252,252,237,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,54,227,253,252,239,233,252,57,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,60,224,252,253,252,202,84,252,253,122,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,163,252,252,252,253,252,252,96,189,253,167,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,51,238,253,253,190,114,253,228,47,79,255,168,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,48,238,252,252,179,12,75,121,21,0,0,253,243,50,0,0,0,0,0,0,0,0,0,0,0,0,0,38,165,253,233,208,84,0,0,0,0,0,0,253,252,165,0,0,0,0,0,0,0,0,0,0,0,0,7,178,252,240,71,19,28,0,0,0,0,0,0,253,252,195,0,0,0,0,0,0,0,0,0,0,0,0,57,252,252,63,0,0,0,0,0,0,0,0,0,253,252,195,0,0,0,0,0,0,0,0,0,0,0,0,198,253,190,0,0,0,0,0,0,0,0,0,0,255,253,196,0,0,0,0,0,0,0,0,0,0,0,76,246,252,112,0,0,0,0,0,0,0,0,0,0,253,252,148,0,0,0,0,0,0,0,0,0,0,0,85,252,230,25,0,0,0,0,0,0,0,0,7,135,253,186,12,0,0,0,0,0,0,0,0,0,0,0,85,252,223,0,0,0,0,0,0,0,0,7,131,252,225,71,0,0,0,0,0,0,0,0,0,0,0,0,85,252,145,0,0,0,0,0,0,0,48,165,252,173,0,0,0,0,0,0,0,0,0,0,0,0,0,0,86,253,225,0,0,0,0,0,0,114,238,253,162,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,85,252,249,146,48,29,85,178,225,253,223,167,56,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,85,252,252,252,229,215,252,252,252,196,130,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,28,199,252,252,253,252,252,233,145,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,25,128,252,253,252,141,37,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
  
  // bbox_find(img);
  printf("%d\n", python_loop_count(arr, 28, 28));
}