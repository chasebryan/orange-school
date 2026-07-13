#include "owned_buffer.h"

#include <inttypes.h>
#include <stdio.h>

#define CHECK(condition)                                                        \
    do {                                                                        \
        if (!(condition)) {                                                     \
            fprintf(stderr, "C check failed at line %d: %s\n", __LINE__,      \
                    #condition);                                                \
            return 1;                                                           \
        }                                                                       \
    } while (0)

static int check_normal_move_wipe_destroy(void) {
    uint8_t source[] = {1, 2, 3, 4};
    const uint8_t original[] = {1, 2, 3, 4};
    struct sys102_buffer owner = SYS102_BUFFER_INIT;
    uint64_t sum = UINT64_C(99);
    size_t index;

    CHECK(sys102_buffer_clone(source, 4, &owner) == SYS102_OK);
    CHECK(owner.data != NULL);
    CHECK(owner.data != source);
    CHECK(owner.len == 4);
    CHECK(sys102_buffer_sum(&owner, &sum) == SYS102_OK);
    CHECK(sum == 10);

    owner.data[1] = 9;
    CHECK(source[1] == original[1]);
    CHECK(sys102_buffer_sum(&owner, &sum) == SYS102_OK);
    CHECK(sum == 17);

    CHECK(sys102_buffer_wipe(&owner) == SYS102_OK);
    for (index = 0; index < owner.len; ++index) {
        CHECK(owner.data[index] == 0);
    }
    for (index = 0; index < sizeof(source); ++index) {
        CHECK(source[index] == original[index]);
    }

    CHECK(sys102_buffer_destroy(&owner) == SYS102_OK);
    CHECK(owner.data == NULL);
    CHECK(owner.len == 0);
    CHECK(sys102_buffer_destroy(&owner) == SYS102_OK);
    return 0;
}

static int check_boundaries(void) {
    uint8_t maximum[SYS102_MAX_BYTES];
    struct sys102_buffer empty = SYS102_BUFFER_INIT;
    struct sys102_buffer owner = SYS102_BUFFER_INIT;
    uint64_t sum = UINT64_C(77);
    size_t index;

    CHECK(sys102_buffer_clone(NULL, 0, &empty) == SYS102_OK);
    CHECK(sys102_buffer_sum(&empty, &sum) == SYS102_OK);
    CHECK(sum == 0);
    CHECK(sys102_buffer_wipe(&empty) == SYS102_OK);
    CHECK(sys102_buffer_destroy(&empty) == SYS102_OK);

    for (index = 0; index < SYS102_MAX_BYTES; ++index) {
        maximum[index] = UINT8_MAX;
    }
    CHECK(sys102_buffer_clone(maximum, SYS102_MAX_BYTES, &owner) == SYS102_OK);
    CHECK(sys102_buffer_sum(&owner, &sum) == SYS102_OK);
    CHECK(sum == UINT64_C(32) * UINT8_MAX);
    CHECK(sys102_buffer_destroy(&owner) == SYS102_OK);
    return 0;
}

static int check_invalid_inputs(void) {
    uint8_t source[SYS102_MAX_BYTES + 1] = {0};
    struct sys102_buffer owner = SYS102_BUFFER_INIT;
    struct sys102_buffer occupied = SYS102_BUFFER_INIT;
    struct sys102_buffer invalid = {NULL, 1};
    uint64_t sum = UINT64_C(1234);

    CHECK(sys102_buffer_clone(source, SYS102_MAX_BYTES + 1, &owner)
          == SYS102_LENGTH_ERROR);
    CHECK(owner.data == NULL && owner.len == 0);
    CHECK(sys102_buffer_clone(NULL, 1, &owner) == SYS102_NULL_POINTER);
    CHECK(owner.data == NULL && owner.len == 0);
    CHECK(sys102_buffer_clone(source, 1, NULL) == SYS102_NULL_POINTER);

    CHECK(sys102_buffer_clone(source, 1, &occupied) == SYS102_OK);
    CHECK(sys102_buffer_clone(source, 1, &occupied) == SYS102_STATE_ERROR);
    CHECK(occupied.data != NULL && occupied.len == 1);
    CHECK(sys102_buffer_destroy(&occupied) == SYS102_OK);

    CHECK(sys102_buffer_sum(NULL, &sum) == SYS102_NULL_POINTER);
    CHECK(sum == UINT64_C(1234));
    CHECK(sys102_buffer_sum(&owner, NULL) == SYS102_NULL_POINTER);
    CHECK(sys102_buffer_sum(&invalid, &sum) == SYS102_STATE_ERROR);
    CHECK(sum == UINT64_C(1234));
    CHECK(sys102_buffer_wipe(NULL) == SYS102_NULL_POINTER);
    CHECK(sys102_buffer_wipe(&invalid) == SYS102_STATE_ERROR);
    CHECK(sys102_buffer_destroy(NULL) == SYS102_NULL_POINTER);
    CHECK(sys102_buffer_destroy(&invalid) == SYS102_STATE_ERROR);
    CHECK(invalid.data == NULL && invalid.len == 1);
    return 0;
}

int main(void) {
    CHECK(check_normal_move_wipe_destroy() == 0);
    CHECK(check_boundaries() == 0);
    CHECK(check_invalid_inputs() == 0);
    puts("c sys102 ownership tests: PASS");
    return 0;
}
