#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>

typedef struct Data_ {
  long* arr;
  int* frames;
} Data;

long* createArray() {
  long* arr = malloc(10000 * sizeof(long));
  for (long i = 0; i < 10000; i++) {
    arr[i] = i;
  }

  return arr;
}

void* processArray(void* data) {
  Data* new_data = data;

  int* frames = new_data->frames;
  int start = frames[0];
  int end = frames[1];

  printf("%d, %d\n", start, end);
  long* arr = new_data->arr;

  for (int i = start; i < end; i++) {
    arr[i] = (long) pow(arr[i], 3);
    // arr[i] = sqrt(cos(sqrt(arr[i])) * sin(sqrt(arr[i])));
  }
  sleep(5000);
  free(new_data->frames);
  free(new_data);
  return 0;
}

int main() {
  long* arr = createArray();

  for (int i = 0; i < 10000; i++) {
    printf("%ld ", arr[i]);
  }

  printf("Output\n");

  int offset = 0;
  pthread_t tid;
  for (int i = 0; i < 4; i++) {
    Data* new_data = malloc(sizeof(Data));
    int* frames = malloc(2 * sizeof(int));

    frames[0] = offset;
    frames[1] = offset + 2500;

    new_data->arr = arr;
    new_data->frames = frames;

    pthread_create(&tid, NULL, processArray, new_data);
    offset += 2500;
  }
  
  for (int i = 0; i < 10000; i++) {
    printf("%ld ", arr[i]);
  }
}