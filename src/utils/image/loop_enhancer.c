#include <stdlib.h>
#include <stdio.h>
#include "../../header/error.h"
#include "../../header/image.h"
#include "../../header/stack.h"
#include "../../header/loop_enhancer.h"


static int max(int a, int b) {
  // if a - b >= 0 then a - b >> 31 = 0, therefore yield a
  // if a - b << 0 then a - b >> 31 = -1, therefore yield b
  return a - ((a - b) & (a - b) >> (sizeof(a) * 8 - 1));
}

static int min(int a, int b) {
  // if a < b, then -a > -b, therefore min(a, b) = max(-a, -b)
  return -1 * max(-a, -b);
}

loopEnhnacer *loop_enhancer_init(IMAGE img)
{
    // initialize memory
    loopEnhnacer *enhancer = malloc(sizeof(loopEnhnacer));
    checkmem(enhancer);

    STACK s = stack_init();

    uint8_t* dp = calloc((img->nx * img->ny), sizeof(uint8_t));
    checkmem(dp);

    enhancer->img = img;
    enhancer->s = s; // stack
    enhancer->dp = dp;

    return enhancer;
}

static int is_BG(uint8_t val) 
{
    return val <= BG_PIXELS_UPPER;
}

static int is_not_BG(uint8_t val)
{
    return val > BG_PIXELS_UPPER;
}

static int update_pos_min(int j) 
{
    return j - 1;
}

static int update_pos_plus(int j)
{
    return j + 1;
}

static int is_part_of_other_region(loopEnhnacer* enhancer, int i, int j) 
{
    return image_read_serial(
        enhancer->dp, enhancer->img->nx, i, j) != 0;
}

// static int is_outer(loopEnhnacer* enhancer, int i, int j) 
// {
//     return image_read_serial(
//         enhancer->dp, enhancer->img->nx, i, j) == 4;
// }

static int sweep(loopEnhnacer* enhancer, int i, int j, update_fnc f, condition_fnc c, int end_pos, int label, int id) {
    uint8_t pix_intensity = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    while (j != end_pos && c(pix_intensity)) 
    {
        if (is_part_of_other_region(enhancer, i, j)) break;

        if (label) 
            image_write_serial(enhancer->dp, enhancer->img->nx, i, j, id);

        j = f(j);
        pix_intensity = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    }

    // j is either end pos
    // or j is not BG
    // or part of other region
    return j;
}

static void find_interval(int* dst, loopEnhnacer* enhancer, int i, int j, int mode, int label, int id) 
{
    // find interval where pixels 
    // mode = 0 -> pixels == BG
    // mode = 1 -> pixels == not BG
    // if label is specified, when sweeping, it will label the pixel pos
    // in dp as 1, if not, sweep will just sweep

    condition_fnc f; // function to evaluate pixel
    if (mode) 
        f = is_not_BG;
    else
        f = is_BG;
        
    if (label) 
    {
        // label start position
        image_write_serial(enhancer->dp, enhancer->img->nx, i, j, id);
    }

    int j_start = sweep(enhancer, i, j - 1, update_pos_min, f, -1, label, id) + 1;
    int j_end = sweep(enhancer, i, j + 1, update_pos_plus, f, enhancer->img->nx, label, id) - 1;

    dst[0] = j_start;
    dst[1] = j_end;

}

static void label_outer(loopEnhnacer* enhancer, int i_start,int j_entry, update_fnc f, int end_pos, int id) 
{
    uint8_t pix;
    int i, j, j_start, j_end, j_start_curr, j_end_curr, cnt;
    int dst[2] = {0, 0};

    cnt = 0;
    i = f(i_start);
    if (i == end_pos) return;
    
    j = j_entry;

    // init interval
    find_interval(dst, enhancer, i, j_entry, 1, 1, id);
    j_start = dst[0];
    j_end = dst[1];

    // start
    i = f(i);
    while (i != end_pos)
    {
        j_entry = -1;
        for (j = j_start; j <= j_end; j++) 
            {
                pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
                if (pix > BG_PIXELS_UPPER) {
                    if (j_entry != -1) break;
                    j_entry = j;
                }
            }

            // region is terminated here
            if (j_entry == -1) break;

            // update interval 
            find_interval(dst, enhancer, i, j, 1, 1, id);
            j_start_curr = dst[0];
            j_end_curr = dst[1];

            if (j_end_curr - j_start_curr == j_end - j_start)
                cnt += 1;

            else
                cnt = 0;
            
            // Terminate
            if (j_end_curr - j_start_curr > j_end - j_start) break;
            if (cnt > (MAXIMUM_COUNT - 1)) break;
            
            j_start = j_start_curr;
            j_end = j_end_curr;

            i = f(i);
    }
}

static void label_inner(loopEnhnacer* enhancer, int i, int j_start, int j_end, int id) 
{
    int j;
    uint8_t pix;

    j = j_start - 1;
    pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    while (pix > BG_PIXELS_UPPER) 
    {
        image_write_serial(enhancer->dp, enhancer->img->nx, i, j, id);
        j -= 1;
        pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    }

    j = j_end + 1;
    pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    while (pix > BG_PIXELS_UPPER) 
    {
        image_write_serial(enhancer->dp, enhancer->img->nx, i, j, id);
        j += 1;
        pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
    }
}

static void fill(loopEnhnacer* enhancer) {
    DATA data;
    DATA data_frames;
    STACK frames;
    int i_start, j_start, j_end, j_entry, j_start_curr, j_end_curr;
    int i_min, i_max, temp;
    int s, e, is_unique, temp_id, id;
    uint8_t pix;

    int interval[] = {0, 0};
    temp_id = 1;
    id = 1;
    while (!stack_is_empty(enhancer->s))
    {
        data = stack_pop(enhancer->s);
        i_start = data->i;
        j_start = data->j_start;
        j_end = data->j_end;
        free(data);

        // store head data to stack
        data_frames = malloc(sizeof(Data));
        data_frames->i = i_start - 1;
        data_frames->j_start = j_start;
        data_frames->j_end = j_end;
        
        i_min = i_start;
        temp = j_start;
        if (is_part_of_other_region(enhancer, i_start, j_start)) continue;
        i_start++;

        // create new frames
        frames = stack_init();
        stack_push(frames, data_frames);
        is_unique = 1;

        while (i_start < enhancer->img->ny) {
            // find entry point
            j_entry = -1;
            s = max(0, j_start - 1);
            e = min(j_end + 2, enhancer->img->nx);
            for (int j = s; j < e; j++) 
            {
                pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i_start, j);
                if (pix <= BG_PIXELS_UPPER) {
                    j_entry = j;
                    break;
                }
            }

            // region is terminated here
            if (j_entry == -1)
            {
                // store last data to stack
                data_frames = malloc(sizeof(Data));
                data_frames->i = i_start - 1;
                data_frames->j_start = j_start;
                data_frames->j_end = j_end;
                stack_push(frames, data_frames);
                break;
            } 

            find_interval(interval, enhancer, i_start, j_entry, 0, 0, 0);

            // unpack value
            j_start_curr = interval[0];
            j_end_curr = interval[1];

            // if (j_start_curr > j_end + 1) break;
            // if (j_end_curr < j_start - 1) break;

            // check if region is connected to other region
            if (is_part_of_other_region(enhancer, i_start, j_start_curr)) 
            {
                // if (is_outer(enhancer, i_start, j_start_curr)) 
                // {
                //     is_unique = 0;
                // }
                // else {
                //     temp_id = id;
                //     id = image_read_serial(enhancer->dp, enhancer->img->nx, i_start, j_start_curr);
                // }

                temp_id = id;
                id = image_read_serial(enhancer->dp, enhancer->img->nx, i_start, j_start_curr);
                break;
            }

            if (is_part_of_other_region(enhancer, i_start, j_end_curr)) {
                // if (is_outer(enhancer, i_start, j_end_curr))
                // {
                //     is_unique = 0;
                // }
                // else {
                //     temp_id = id;
                //     id = image_read_serial(enhancer->dp, enhancer->img->nx, i_start, j_end_curr);
                // }
                temp_id = id;
                id = image_read_serial(enhancer->dp, enhancer->img->nx, i_start, j_end_curr);
                break;
            }

            // region is connected
            if (j_end_curr == enhancer->img->nx - 1 || j_start == 0) {
                is_unique = 0;
                break;
            }

            j_start = j_start_curr;
            j_end = j_end_curr;
            
            // store data to stack
            data_frames = malloc(sizeof(Data));
            data_frames->i = i_start;
            data_frames->j_start = j_start;
            data_frames->j_end = j_end;
            stack_push(frames, data_frames);

            i_start++;
        }
        i_max = i_start - 1;
        if (is_unique) 
        {
            while (!stack_is_empty(frames))
            {
                data_frames = stack_pop(frames);

                // unpack data
                i_start = data_frames->i;
                j_start = data_frames->j_start;
                j_end = data_frames->j_end;

                for (int j = j_start; j < j_end + 1; j++) 
                {
                    image_write_serial(
                        enhancer->dp, enhancer->img->nx, 
                        i_start, j, 1
                    );
                
                }

                free(data_frames);
                // label loop pixels
                label_inner(enhancer, i_start, j_start, j_end, id);
                label_outer(enhancer, i_min, temp, update_pos_min, -1, id);
                label_outer(enhancer, i_max, temp, update_pos_plus, enhancer->img->ny, id);
            }
            if (id < temp_id) 
                {
                    id = temp_id;
                } else
                {
                    id += 1;
                    temp_id = id;
                } 
        }
        // destroy all leftover contents in stack
        stack_destroy(frames);
    }
}

static int is_exist_upper(loopEnhnacer* enhancer, int i, int j) 
{
    int pix;
    for (int k = -1; k < 2; k++) 
    {
        if (j + k < 0 || j + k >= enhancer->img->nx) continue;
        pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i - 1, j + k);
        if (pix <= BG_PIXELS_UPPER) return 1;
    }

    return 0;
}


static void init_stack(loopEnhnacer* enhancer) 
{
    int i, j, pix;
    int jr, jsr;
    int exist_upper;
    DATA u;
    for (i = 1; i < enhancer->img->ny; i++) {
        j = 0;
        while (j < enhancer->img->nx) 
        {
            pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
            // image_write_serial(enhancer->dp, enhancer->img->nx, i, j, 4);
            if (pix > BG_PIXELS_UPPER) 
            {
                jr = j; // start region
                exist_upper = 0;
                while (jr < enhancer->img->nx && pix > BG_PIXELS_UPPER) 
                {
                    jr++;
                    pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, jr);
                }

                jsr = jr;
                while (jsr < enhancer->img->nx && pix <= BG_PIXELS_UPPER) 
                {
                    if (is_exist_upper(enhancer, i, jsr))  exist_upper = 1;
                    jsr++;
                    pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, jsr);
                }

                if (jsr == enhancer->img->nx) break;

                // not part of any other region
                if (!exist_upper) {
                    DATA data = malloc(sizeof(Data));
                    data->i = i;
                    data->j_start = jr;
                    data->j_end = jsr - 1;
                    stack_push(enhancer->s, (void*) data);
                }

                // check if part of upper region 
                // but not connected
                u = stack_peek(enhancer->s);
                if (exist_upper && !stack_is_empty(enhancer->s) && enhancer->s->head->next && u->i == i) 
                {
                    DATA data = malloc(sizeof(Data));
                    data->i = i;
                    data->j_start = jr;
                    data->j_end = jsr - 1;
                    stack_push(enhancer->s, (void*) data);
                }

                j = jsr;
            } else 
            {
                j += 1;
            }
        }
    }
}

void loop_enhance(loopEnhnacer *enhancer)
{
    init_stack(enhancer); // create stack
    fill(enhancer); // fill dp
    uint8_t pix;
    int t;
    for (int i = 0; i < enhancer->img->ny; i++) {
        for (int j = 0; j < enhancer->img->nx; j++) {
            pix = image_read_serial(enhancer->img->img, enhancer->img->nx, i, j);
            if (pix > BG_PIXELS_UPPER) 
            {
                t = image_read_serial(enhancer->dp, enhancer->img->nx, i, j);
                // printf("%d\n", t);
                switch (t)
                {
                    case 1:
                        pix = DATA_LOOP_PIXEL_INTENSITY_FIRST;
                        break;
                    case 2:
                    case 3:
                        pix = DATA_LOOP_PIXEL_INTENSITY_LAST;
                        break;
                    default:
                        pix = DATA_PIXEL_INTENSITY;
                        break;
                }

                image_write_serial(
                    enhancer->img->img, 
                    enhancer->img->nx, 
                    i, j, pix
                );
            }
        }
    }

    // clear memory before exiting
    free(enhancer->dp);
    stack_destroy(enhancer->s);
    free(enhancer);
}
void python_loop_enhance(uint8_t *img, int nx, int ny)
{
    // IMAGE img_data = python_read_image(img, nx, ny);
    IMAGE img_data = malloc(sizeof(Image));
    img_data->img = img;
    img_data->nx = nx;
    img_data->ny = ny;
    
    loopEnhnacer *enhancer = loop_enhancer_init(img_data);
    loop_enhance(enhancer);
    // free struct
    free(img_data);
}