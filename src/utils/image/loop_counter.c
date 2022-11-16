#include <stdlib.h>
#include <stdio.h>
#include "../../header/error.h"
#include "../../header/image.h"
#include "../../header/stack.h"
#include "../../header/loop_counter.h"

typedef struct Data_
{
    POS pos;
    int direction;
} Data;

typedef Data *DATA;

static void update_pos_left(POS pos)
{
    pos->j--;
}

static void update_pos_dowm(POS pos)
{
    pos->i--;
}

static void update_pos_right(POS pos)
{
    pos->j++;
}

static void update_pos_up(POS pos)
{
    pos->i++;
}

static updatePos update_fnc[4] = {
    update_pos_left,
    update_pos_dowm,
    update_pos_right,
    update_pos_up,
};

static int equal_end_pos(POS a, POS end_pos)
{
    if (end_pos->i == -2)
    {
        return end_pos->j == a->j;
    }

    if (end_pos->j == -2)
    {
        return end_pos->i == a->i;
    }

    return (end_pos->i == a->i && end_pos->j == a->j);
}

loopCounter *loop_counter_init(IMAGE img)
{
    loopCounter *counter = malloc(sizeof(loopCounter));
    counter->img = img;
    uint8_t *dp = calloc(img->nx * img->ny, sizeof(uint8_t));
    STACK s = stack_init();
    POS *end_pos = malloc(4 * sizeof(POS));

    // initialize end position
    // end pos left
    POS end_pos_left = malloc(sizeof(Position));
    end_pos_left->i = -2;
    end_pos_left->j = -1;
    end_pos[0] = end_pos_left;

    // end pos left
    POS end_pos_down = malloc(sizeof(Position));
    end_pos_down->i = -1;
    end_pos_down->j = -2;
    end_pos[1] = end_pos_down;

    // end pos right
    POS end_pos_right = malloc(sizeof(Position));
    end_pos_right->i = -2;
    end_pos_right->j = img->nx;
    end_pos[2] = end_pos_right;

    // end pos up
    POS end_pos_up = malloc(sizeof(Position));
    end_pos_up->i = img->ny;
    end_pos_up->j = -2;
    end_pos[3] = end_pos_up;

    counter->img = img;
    counter->update_fnc = update_fnc;
    counter->end_pos = end_pos;
    counter->dp = dp;
    counter->s = s; // stack

    return counter;
}

static int sameRegion(int* vec_a, int* vec_b) {
    // boundary
    if (vec_a[0] == 0 && vec_a[1] == 0) return 0;
    if (vec_b[0] == 0 && vec_b[1] == 0) return 0;
    // 0 degree angle
    if ((vec_a[0] == vec_b[0]) && (vec_a[1] == vec_b[1])) return 1;
    // 45 and 90 degree angle
    if (vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1] >= 0) return 1;

    return 0;
}

static void boundaryVector(loopCounter *counter, POS pos, int* vec)
{
    if (!vec) die("NullPointerException: Accessing a null pointer");
    vec[0] = 0; vec[1] = 0; // initialize vector
    if (pos->i < 0 || pos->i >= counter->img->ny)
        return;
    if (pos->j < 0 || pos->j >= counter->img->nx)
        return;
    if (image_read_serial(counter->img->img, counter->img->nx, pos->i, pos->j) == BG_PIXELS_INTENSITY)
        return;

    int a, b;
    int pos_i, pos_j;
    uint8_t pix_intensity;
    int dx[3] = {-1, 0, 1};
    int dy[3] = {-1, 0, 1};


    // int* vec = NULL;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            pos_i = pos->i + dy[i];
            pos_j = pos->j + dx[j];

            pix_intensity = image_read_serial(counter->img->img, counter->img->nx, pos_i, pos_j);
            if (pix_intensity == BG_PIXELS_INTENSITY || pos_i < 0 || pos_i == counter->img->ny || pos_j < 0 || pos_j == counter->img->nx) {
                // if (!vec) {
                //     vec = calloc(2, sizeof(int));
                // }
                a = vec[0] + dy[i];
                b = vec[1] + dx[j];
                vec[0] = a <= 1 && a >= -1 ? a : vec[0];
                vec[1] = b <= 1 && b >= -1 ? b : vec[1];
            }
        }
    }
}

static int isBoundary(int* vec) {
    return !(vec[0] == 0 && vec[1] == 0);
}

static int *getNeighborBoundary(loopCounter *counter, POS pos, int* curr_vec)
{
    int dy, dx, c;
    c = 0;
    int ds[4] = {-1, 0, 1, 0};

    int *loc = malloc(4 * sizeof(int));
    loc[0] = -1;
    loc[1] = -1;
    loc[2] = -1;
    loc[3] = -1;

    POS curr_loc = malloc(sizeof(Position));
    curr_loc->i = pos->i;
    curr_loc->j = pos->j;
    int* vec = calloc(2, sizeof(int));

    for (int k = 0; k < 4; k++)
    {
        dy = ds[(k + 3) % 4];
        dx = ds[k];

        curr_loc->i = pos->i + dy;
        curr_loc->j = pos->j + dx;

        if (curr_loc->i < 0 || curr_loc->i == counter->img->ny)
            continue;
        if (curr_loc->j < 0 || curr_loc->j == counter->img->nx)
            continue;

        boundaryVector(counter, curr_loc, vec);
        if (isBoundary(vec))
        {
            if (image_read_serial(counter->dp, counter->img->nx, curr_loc->i, curr_loc->j)) {
                continue;
            }
            if (!sameRegion(vec, curr_vec)) {
                continue;
            }
            loc[c] = k;
            c++;
        }
    }

    free(vec);
    free(curr_loc);
    return loc;
}

static void find_new_node(loopCounter* counter, POS curr_loc, int* curr_vec, int direction) {
    int *directions;
    int i;
    int exist = 0;
    directions = getNeighborBoundary(counter, curr_loc, curr_vec);
    i = 0;

    while (directions[i] != -1)
    {
        if (directions[i] != direction)
        {
            exist = 1;
            break;
        }
        i++;
    }

    if (exist)
    {
        POS new_loc = malloc(sizeof(Position));
        new_loc->i = curr_loc->i;
        new_loc->j = curr_loc->j;
        i = 0;
        while (directions[i] != -1)
        {
            if (directions[i] != direction)
            {
                DATA new_data = malloc(sizeof(Data));
                new_data->pos = new_loc;
                new_data->direction = directions[i];
                stack_push(counter->s, new_data);
            }
            i++;
        }
    }
    free(directions);
}

static void tranverse(loopCounter *counter)
{
    DATA data;
    POS end_pos;
    POS root_pos;
    int *curr_vec = calloc(2, sizeof(int));
    int *last_vec = calloc(2, sizeof(int));
    POS curr_loc = malloc(sizeof(Position)); // temp variables
    while (!stack_is_empty(counter->s))
    {
        data = stack_pop(counter->s);

        root_pos = data->pos;
        int direction = data->direction;

        end_pos = counter->end_pos[direction];
        curr_loc->i = root_pos->i;
        curr_loc->j = root_pos->j;

        // update position
        counter->update_fnc[direction](curr_loc);

        // initialize vector
        boundaryVector(counter, curr_loc, curr_vec);
        last_vec[0] = curr_vec[0];
        last_vec[1] = curr_vec[1];

        while (!equal_end_pos(curr_loc, end_pos) && isBoundary(curr_vec))
        {
            if (!sameRegion(curr_vec, last_vec)) {
                find_new_node(counter, curr_loc, last_vec, direction);
                break;
            }

            image_write_serial(counter->dp, counter->img->nx, curr_loc->i, curr_loc->j, 1);
            find_new_node(counter, curr_loc, curr_vec, direction);

            last_vec[0] = curr_vec[0];
            last_vec[1] = curr_vec[1];

            counter->update_fnc[direction](curr_loc);
            // update curr_vec
            boundaryVector(counter, curr_loc, curr_vec);
        }

        // delete unused memory
        // free(data->pos);
        free(data);
    }

    free(curr_loc);
    free(curr_vec);
    free(last_vec);
}
int loop_count(loopCounter *counter)
{
    int c;
    int outline_count = 0;
    int* vec = calloc(2, sizeof(int));
    for (int i = 0; i < counter->img->ny; i++)
    {
        for (int j = 0; j < counter->img->nx; j++)
        {
            if (image_read_serial(counter->img->img, counter->img->nx, i, j) != BG_PIXELS_INTENSITY)
            {
                if (!image_read_serial(counter->dp, counter->img->nx, i, j))
                {
                    // printf("passed dp. %d %d\n", i, j);
                    POS start_pos = malloc(sizeof(Position));
                    start_pos->i = i;
                    start_pos->j = j;
                    boundaryVector(counter, start_pos, vec);
                    if (isBoundary(vec))
                    {
                        // printf("passed vec: i = %d, j = %d, x = %d, y = %d\n", i, j, vec[0], vec[1]);
                        // update dp
                        image_write_serial(counter->dp, counter->img->nx, start_pos->i, start_pos->j, 1);
                        // printf("i=%d,j=%d\n", i, j);
                        // printf("x=%d,y=%d\n", vec[0], vec[1]);
                        int *dirs = getNeighborBoundary(counter, start_pos, vec);
                        c = 0;
                        outline_count++;
                        // printf("i=%d,j=%d\n", i, j);
                        while (dirs[c] != -1)
                        {
                            DATA new_data = malloc(sizeof(Data));
                            new_data->pos = start_pos;
                            new_data->direction = dirs[c];
                            stack_push(counter->s, new_data);
                            c++;
                        }
                        free(dirs);
                        tranverse(counter);
                    } 
                    else 
                    {
                        free(start_pos);
                    }
                }
            }
        }
    }

    // free all contents in counter
    free(counter->dp);
    free(vec);
    for (int i = 0 ; i < 4; i++) {
        free(counter->end_pos[i]);
    }

    free(counter->end_pos);
    stack_destroy(counter->s);
    // freee counter
    free(counter);

    return outline_count - 1;
}
int python_loop_count(uint8_t *img, int nx, int ny)
{
    IMAGE img_data = python_read_image(img, nx, ny);
    // IMAGE img_data = malloc(sizeof(Image));
    // img_data->img = img;
    // img_data->nx = nx;
    // img_data->ny = ny;
    
    loopCounter *counter = loop_counter_init(img_data);
    int n = loop_count(counter);
    // free struct
    free(img_data);
    return n;
}