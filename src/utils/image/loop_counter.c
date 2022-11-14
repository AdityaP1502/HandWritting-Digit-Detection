#include <stdlib.h>
#include <stdio.h>
#include "error.h"
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

static int isBoundary(loopCounter *counter, POS pos)
{
    int dx[3] = {-1, 0, 1};
    int dy[3] = {-1, 0, 1};
    uint8_t pix_intensity;
    if (pos->i < 0 || pos->i >= counter->img->ny)
        return 0;
    if (pos->j < 0 || pos->j >= counter->img->nx)
        return 0;
    if (image_read_serial(counter->img->img, counter->img->nx, pos->i, pos->j) == BG_PIXELS_INTENSITY)
        return 0;

    int pos_i, pos_j;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            pos_i = pos->i + dy[i];
            pos_j = pos->j + dx[j];

            if (pos_i < 0 || pos_i == counter->img->ny)
                return 1;
            if (pos_j < 0 || pos_j == counter->img->nx)
                return 1;
            pix_intensity = image_read_serial(counter->img->img, counter->img->nx, pos_i, pos_j);
            if (pix_intensity <= BG_PIXELS_INTENSITY && pix_intensity >= (BG_PIXELS_INTENSITY - 5))
                return 1;
        }
    }

    return 0;
}

static int *getNeighborBoundary(loopCounter *counter, POS pos)
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

    for (int k = 0; k < 4; k++)
    {
        dy = ds[(k + 3) % 4];
        dx = ds[k];

        curr_loc->i = pos->i + dy;
        curr_loc->j = pos->j + dx;

        if (curr_loc->i < 0 || curr_loc->i >= counter->img->ny)
            continue;
        if (curr_loc->j < 0 || curr_loc->j >= counter->img->nx)
            continue;

        if (isBoundary(counter, curr_loc))
        {
            if (image_read_serial(counter->dp, counter->img->nx, curr_loc->i, curr_loc->j))
                continue;
            loc[c] = k;
            c++;
        }
    }

    free(curr_loc);
    return loc;
}

static void tranverse(loopCounter *counter)
{
    while (!stack_is_empty(counter->s))
    {
        int *directions;
        int i;
        int exist = 0; // set to false

        DATA data = stack_pop(counter->s);

        POS root_pos = data->pos;
        int direction = data->direction;

        POS end_pos = counter->end_pos[direction];
        POS curr_loc = malloc(sizeof(Position)); // temp variables
        curr_loc->i = root_pos->i;
        curr_loc->j = root_pos->j;

        // update dp
        image_write_serial(counter->dp, counter->img->nx, curr_loc->i, curr_loc->j, 1);

        // update position
        counter->update_fnc[direction](curr_loc);

        while (!equal_end_pos(curr_loc, end_pos) && isBoundary(counter, curr_loc))
        {
            image_write_serial(counter->dp, counter->img->nx, curr_loc->i, curr_loc->j, 1);
            directions = getNeighborBoundary(counter, curr_loc);
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

            counter->update_fnc[direction](curr_loc);
            free(directions);
        }

        // delete unused memory
        free(data);
        free(curr_loc);
        
    }
}

int loop_count(loopCounter *counter)
{
    int c;
    int outline_count = 0;
    for (int i = 0; i < counter->img->ny; i++)
    {
        for (int j = 0; j < counter->img->nx; j++)
        {
            if (image_read_serial(counter->img->img, counter->img->nx, i, j) != BG_PIXELS_INTENSITY)
            {
                if (!image_read_serial(counter->dp, counter->img->nx, i, j))
                {
                    POS start_pos = malloc(sizeof(Position));
                    start_pos->i = i;
                    start_pos->j = j;
                    if (isBoundary(counter, start_pos))
                    {
                        int *dirs = getNeighborBoundary(counter, start_pos);
                        c = 0;
                        outline_count++;
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
                }
            }
        }
    }

    // free all contents in counter
    free(counter->dp);
    free(counter->end_pos);
    stack_destroy(counter->s);
    // freee counter
    free(counter);

    return outline_count - 1;
}

int python_loop_count(uint8_t *img, int nx, int ny)
{
    IMAGE img_data = python_read_image(img, nx, ny);

    loopCounter *counter = loop_counter_init(img_data);
    int n = loop_count(counter);

    // free copy of images
    free(img_data->img);
    // free struct
    free(img_data);

    return n;
}