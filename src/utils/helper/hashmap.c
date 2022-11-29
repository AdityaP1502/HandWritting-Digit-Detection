#include <stdlib.h>
#include <stdint.h>

#include "../../header/error.h"
#include "../../header/dynamicarray.h"
#include "../../header/hashmap.h"

uint32_t DEFAULT_HASH(void* key) {
    // Used this when key is an integer
    // Defaulh hash used multiplication method 
    uint32_t key_val = *(uint32_t*) key;
    double A = 0.6180339887498949;
    double intermediate_value = (key_val * A);

    // because A is less than 1 then key * A will be less than key
    // therefore key * A will be less than the maximum value of uint32
    intermediate_value = intermediate_value - (uint32_t)(intermediate_value);

    uint32_t hash = (uint32_t) (intermediate_value * DEFAULT_NUMBER_OF_BUCKETS); // strip the decimal part
    return hash;
}

int DEFAULT_COMPARE(void* a, void* b) {
    uint32_t a_val = *(uint32_t*) a;
    uint32_t b_val = *(uint32_t*) b;
    return a_val == b_val;
}

MAP Hashmap_create(Hashmap_compare cmp, Hashmap_hash hash, destroyFnc destroy) {
    MAP new_map = malloc(sizeof(Hashmap));
    checkmem(new_map);

    if (!cmp) {
        new_map->cmp = DEFAULT_COMPARE;
    } else {
        new_map->cmp = cmp;
    }

    if (!hash) {
        new_map -> hash = DEFAULT_HASH;
    } else {
        new_map->hash = DEFAULT_HASH;
    }

    // initialize buckets
    new_map->destroy = destroy;
    if (!destroy) new_map->destroy = DEFAULT_DESTROY;
    
    new_map->buckets = DynArr_create(DEFAULT_NUMBER_OF_BUCKETS, 0, destroy);
    new_map->length = 0;
    return new_map;
}

void Hashmap_destroy(MAP map) {
    // free all data inside the buckets
    if (map) {
        for (int i = 0; i < DynArr_length(map->buckets); i++) {
            dArr bucket = DynArr_get(map->buckets, i); // get list of all node stored in bucket
            if (bucket) {
                for (int j = 0; j < DynArr_length(bucket); j++) {
                    // delete all content stored in node
                    HashmapNode* node = DynArr_get(bucket, j);
                    free(node->key);
                    map->destroy(node->data);
                }
                // destroy the bucket
                DynArr_destroy(&bucket);
            }
        }
        // delete the buckets
        free(map->buckets->arr);
        free(map->buckets);
        free(map);
    }
}

HashmapNode* Hashmap_create_node(void* key, void* data, uint32_t hash) {
    HashmapNode* new_node = malloc(sizeof(HashmapNode));
    checkmem(new_node);

    new_node->key = key;
    new_node->data = data;
    new_node->hash = hash;

    return new_node;
}

dArr Hashmap_find_bucket(MAP map, uint32_t idx, int create) {
    dArr bucket = DynArr_get(map->buckets, idx);
    if (!bucket && create) {
        // bucket isn't exist
        // set it up
        bucket = DynArr_create(DEFAULT_NUMBER_OF_BUCKETS, 1, map->destroy);
        
        // store the bucket in the buckets
        DynArr_insert(map->buckets, bucket, idx);

    } else if (!bucket && !create) {
        // no bucket is found
        return NULL;
    }

    return bucket;
}

int Hashmap_get_node(MAP map, dArr bucket, void* key) {
    // tranverse bucket to find entry that match key
    int length = DynArr_length(bucket);
    for (int i = 0; i < length; i++) {
        HashmapNode* node = DynArr_get(bucket, i);
        void* bucket_key = node->key;
        if (map->cmp(key, bucket_key)) return i;
    }

    return -1;
}

void Hashmap_set(MAP map, void* key, void* data) {
    uint32_t idx = map->hash(key); // find the location based on the hash
    dArr bucket = Hashmap_find_bucket(map, idx, 1);
    int node_idx = Hashmap_get_node(map, bucket, key);

    if (node_idx < 0) {
        // key hasn't been set before
        HashmapNode* new_node = Hashmap_create_node(key, data, idx);
        // push item into the bucket
        DynArr_append(bucket, new_node);
        map->length++;
        return;
    }
    // overwrite key value
    HashmapNode* node = DynArr_get(bucket, node_idx);
    free(node->data); // delete useless data
    node->data = data; // overwrite the data
}



void* Hashmap_get(MAP map, void* key, void* default_value) {
    // find bucket
    uint32_t hash = map->hash(key);
    dArr bucket = Hashmap_find_bucket(map, hash, 0);

    if (!bucket) return default_value;
    
    int idx = Hashmap_get_node(map, bucket, key);

    if (idx < 0) return default_value;

    HashmapNode* node = DynArr_get(bucket, idx);
    return node->data;
} 

void* Hashmap_delete(MAP map, void* key) {
    // find bucket
    uint32_t hash = map->hash(key);
    dArr bucket = Hashmap_find_bucket(map, hash, 0);
    int idx = Hashmap_get_node(map, bucket, key);
    void* pop_data = DynArr_get(bucket, idx);

    // remove data from the bucket
    DynArr_remove(bucket, idx);
    map->length--;
    return pop_data;
}

int Hashmap_length(MAP map) {
    return map->length;
}