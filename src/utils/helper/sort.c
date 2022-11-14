#include <stdio.h>
#include "../../header/error.h"
#include "../../header/sort.h"

static void swap(void** a, void** b) {
    void* temp = *(a);
    *a = *b;
    *b = temp; 
}

static void bubbleSort(void** arr, int n, compareFnc cmp) {
    int swapped;
    for (int i = 0; i < n - 1; i++) {
        swapped = 0;
        for (int j = 0; j < n - (i + 1); j++) {
            if (cmp(arr[j + 1], arr[j])) {
                swap(&arr[j + 1], &arr[j]);
                swapped = 1;
            }
        }

        // no swapped element occured in inner loop, break the outer loop
        // array already sorted
        if (!swapped) break;
    }
}


static int quicksort_partition(void** arr, int lo, int hi, compareFnc cmp) {
    // partition array using Hoare's partition scheme
    void* pivot = arr[lo];
    int i = lo - 1; // left index
    int j = hi + 1; // right index

    while (1) {
        // find a value in left side greater 
        // than pivot
        do {
            i++;
        } while (cmp(arr[i], pivot));

        // find value in right side smaller
        // than pivot
        do {
            j--;
        } while(cmp(pivot, arr[j]));

        if (i >= j) {
            return j;
        }

        swap(&arr[i], &arr[j]);
    }
}

static void quickSort(void** arr, int low, int high, compareFnc cmp) {
    if (low < high) {
        /* pi is partitioning index, arr[p] is now
           at right place */
        int pi = quicksort_partition(arr, low, high, cmp);
 
        // Separately sort elements before
        // partition and after partition
        quickSort(arr, low, pi, cmp);
        quickSort(arr, pi + 1, high, cmp);
    }
}

void array_sort(void** arr, int n, compareFnc cmp) {
    if (n < 20) {
        // use bubblesort
        bubbleSort(arr, n, cmp);
    }

    // use quicksort
    quickSort(arr, 0, n - 1, cmp);
}
