#include "bounded_sum.h"

#include <stddef.h>
#include <stdint.h>

#if !defined(__STDC_VERSION__) || __STDC_VERSION__ < 201710L
#error "bounded_sum.c requires C17 or newer"
#endif

_Static_assert(sizeof(int32_t) == 4, "int32_t must be 32 bits");
_Static_assert(sizeof(int64_t) == 8, "int64_t must be 64 bits");

int bounded_sum_i32(const int32_t *values, size_t len, int64_t *out_sum) {
    if (out_sum == NULL) {
        return BOUNDED_SUM_NULL_POINTER;
    }
    if (len > BOUNDED_SUM_MAX_LEN) {
        return BOUNDED_SUM_LENGTH_ERROR;
    }
    if (len > 0 && values == NULL) {
        return BOUNDED_SUM_NULL_POINTER;
    }

    int64_t sum = 0;
    for (size_t index = 0; index < len; ++index) {
        /*
         * At most eight int32_t values are added. Their mathematical sum fits
         * in int64_t, so this signed addition cannot overflow.
         */
        sum += (int64_t)values[index];
    }

    *out_sum = sum;
    return BOUNDED_SUM_OK;
}
