#include <stdlib.h>
#include <stdio.h>
#include "../../header/error.h"
#include "../../header/image.h"
#include "../../header/stack.h"
#include "../../header/loop_counter.h"

static int max(int a, int b) {
  // if a - b >= 0 then a - b >> 31 = 0, therefore yield a
  // if a - b << 0 then a - b >> 31 = -1, therefore yield b
  return a - ((a - b) & (a - b) >> (sizeof(a) * 8 - 1));
}

static int min(int a, int b) {
  // if a < b, then -a > -b, therefore min(a, b) = max(-a, -b)
  return -1 * max(-a, -b);
}

loopCounter *loop_counter_init(IMAGE img)
{
    // initialize memory
    loopCounter *counter = malloc(sizeof(loopCounter));
    checkmem(counter);

    STACK s = stack_init();

    uint8_t* dp = calloc((img->nx * img->ny), sizeof(uint8_t));
    checkmem(dp);

    counter->img = img;
    counter->s = s; // stack
    counter->dp = dp;

    return counter;
}

static int is_BG(uint8_t val) 
{
    return val == BG_PIXELS_INTENSITY;
}

static int update_j_left(int j) 
{
    return j - 1;
}

static int update_j_right(int j)
{
    return j + 1;
}

static int is_part_of_other_region(loopCounter* counter, int i, int j) 
{
    return image_read_serial(
        counter->dp, counter->img->nx, i, j) != 0;
}

static int sweep(loopCounter* counter, int i, int j, update_fnc f, condition_fnc c, int end_pos) {
    uint8_t pix_intensity = image_read_serial(counter->img->img, counter->img->nx, i, j);
    while (j != end_pos && c(pix_intensity)) 
    {
        if (is_part_of_other_region(counter, i, j)) break;
        j = f(j);
        pix_intensity = image_read_serial(counter->dp, counter->img->nx, i, j);
    }

    // j is either end pos
    // or j is not BG
    // or part of other region
    return j;
}

static void find_interval(int* dst, loopCounter* counter, int i, int j) 
{
    // find interval where pixels is BG
    int j_start = sweep(counter, i, j - 1, update_j_left, is_BG, -1) + 1;
    int j_end = sweep(counter, i, j + 1, update_j_right, is_BG, counter->img->nx) - 1;

    dst[0] = j_start;
    dst[1] = j_end;

}

static int fill(loopCounter* counter) {
    int i_start, j_start, j_end, j_entry, j_start_curr, j_end_curr;
    int region_count;
    int s, e;
    uint8_t pix;
    int interval[] = {0, 0};

    region_count = 0;
    while (!stack_is_empty(counter->s))
    {
        DATA data = stack_pop(counter->s);
        i_start = data->i;
        j_start = data->j_start;
        j_end = data->j_end;
        free(data);

        if (is_part_of_other_region(counter, i_start, j_start)) continue;
        region_count++;
        i_start++;

        while (i_start < counter->img->ny) {
            // find entry point
            j_entry = -1;
            s = max(0, j_start - 1);
            e = min(j_end + 2, counter->img->nx);

            for (int j = s; j < e; j++) 
            {
                pix = image_read_serial(counter->img->img, counter->img->nx, i_start, j);
                if (pix == BG_PIXELS_INTENSITY) {
                    j_entry = j;
                    break;
                }
            }

            // region is terminated here
            if (j_entry == -1) break;

            find_interval(interval, counter, i_start, j_entry);
            // unpack value
            j_start_curr = interval[0];
            j_end_curr = interval[1];

            // if (j_start_curr > j_end + 1) break;
            // if (j_end_curr < j_start - 1) break;

            // check if region is connected to other region
            if (is_part_of_other_region(counter, i_start, j_start_curr)) 
            {
                region_count--;
                break;
            }

            if (is_part_of_other_region(counter, i_start, j_end_curr)) {
                region_count--;
                break;;
            }

            // region is connected
            // update dp 
            for (int j = j_start_curr; j < j_end_curr + 1; j++) 
            {
                image_write_serial(
                    counter->dp, counter->img->nx, 
                    i_start, j, 1
                );
            }

            if (j_end_curr == counter->img->nx - 1 || j_start == 0) {
                region_count--;
                break;
            }

            j_start = j_start_curr;
            j_end = j_end_curr;

            i_start++;
        }

    }

    return region_count;
}

static int is_exist_upper(loopCounter* counter, int i, int j) 
{
    int pix;
    for (int k = -1; k < 2; k++) 
    {
        if (j + k < 0 || j + k >= counter->img->nx) continue;
        pix = image_read_serial(counter->img->img, counter->img->nx, i - 1, j + k);
        if (pix == BG_PIXELS_INTENSITY) return 1;
    }

    return 0;
}

static void init_stack(loopCounter* counter) 
{
    int i, j, pix;
    int jr, jsr;
    int exist_upper;
    DATA u;
    for (i = 1; i < counter->img->ny; i++) {
        j = 0;
        while (j < counter->img->nx) 
        {
            image_write_serial(counter->dp, counter->img->nx, i, j, 1);
            pix = image_read_serial(counter->img->img, counter->img->nx, i, j);
            if (pix != BG_PIXELS_INTENSITY) 
            {
                jr = j; // start region
                exist_upper = 0;
                while (jr < counter->img->nx && pix != BG_PIXELS_INTENSITY) 
                {
                    jr++;
                    pix = image_read_serial(counter->img->img, counter->img->nx, i, jr);
                }

                jsr = jr;
                while (jsr < counter->img->nx && pix == BG_PIXELS_INTENSITY) 
                {
                    if (is_exist_upper(counter, i, jsr))  exist_upper = 1;
                    jsr++;
                    pix = image_read_serial(counter->img->img, counter->img->nx, i, jsr);
                }

                if (jsr == counter->img->nx) break;

                // not part of any other region
                if (!exist_upper) {
                    DATA data = malloc(sizeof(Data));
                    data->i = i;
                    data->j_start = jr;
                    data->j_end = jsr - 1;
                    stack_push(counter->s, (void*) data);
                }

                // check if part of upper region 
                // but not connected
                u = stack_peek(counter->s);
                if (exist_upper && !stack_is_empty(counter->s) && counter->s->head->next && u->i == i) 
                {
                    DATA data = malloc(sizeof(Data));
                    data->i = i;
                    data->j_start = jr;
                    data->j_end = jsr - 1;
                    stack_push(counter->s, (void*) data);
                }

                j = jsr;
            } else 
            {
                j += 1;
            }
        }
    }
}

int loop_count(loopCounter *counter)
{
    init_stack(counter);
    int cnt = fill(counter);

    // clear memory before exiting
    free(counter->dp);
    stack_destroy(counter->s);
    free(counter);

    return cnt;
}

int python_loop_count(uint8_t *img, int nx, int ny)
{
    // IMAGE img_data = python_read_image(img, nx, ny);
    IMAGE img_data = malloc(sizeof(Image));
    img_data->img = img;
    img_data->nx = nx;
    img_data->ny = ny;
    
    loopCounter *counter = loop_counter_init(img_data);
    int n = loop_count(counter);
    // free struct
    free(img_data);
    return n;
}