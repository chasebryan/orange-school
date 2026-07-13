#ifndef ORANGE_SCHOOL_BOUNDED_SUM_H
#define ORANGE_SCHOOL_BOUNDED_SUM_H

#include <stddef.h>
#include <stdint.h>

#define BOUNDED_SUM_MAX_LEN 8

enum bounded_sum_status {
    BOUNDED_SUM_OK = 0,
    BOUNDED_SUM_NULL_POINTER = 1,
    BOUNDED_SUM_LENGTH_ERROR = 2
};

/*
 * Contract:
 * - out_sum may be NULL; otherwise it must point to one writable int64_t.
 *   NULL is rejected with BOUNDED_SUM_NULL_POINTER.
 * - len must be at most BOUNDED_SUM_MAX_LEN.
 * - when len is nonzero, values must point to len readable int32_t objects.
 * - values may be NULL when len is zero.
 * - on success, *out_sum receives the mathematical sum and the function
 *   returns BOUNDED_SUM_OK.
 * - on failure, a valid non-NULL output object is unchanged and a nonzero
 *   status is returned.
 * - no pointer is retained after the call.
 */
int bounded_sum_i32(const int32_t *values, size_t len, int64_t *out_sum);

#endif
