#include "bounded_sum.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

static int failures = 0;

static void require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        failures += 1;
    }
}

int main(void) {
    const int32_t normal[] = {4, -1, 7};
    int64_t output = -99;
    int status = bounded_sum_i32(normal, 3, &output);
    require(status == BOUNDED_SUM_OK, "normal status");
    require(output == 10, "normal sum");

    output = -99;
    status = bounded_sum_i32(NULL, 0, &output);
    require(status == BOUNDED_SUM_OK, "empty status");
    require(output == 0, "empty sum");

    const int32_t maximum[BOUNDED_SUM_MAX_LEN] = {
        INT32_MAX,
        INT32_MAX,
        INT32_MAX,
        INT32_MAX,
        INT32_MAX,
        INT32_MAX,
        INT32_MAX,
        INT32_MAX
    };
    output = -99;
    status = bounded_sum_i32(maximum, BOUNDED_SUM_MAX_LEN, &output);
    require(status == BOUNDED_SUM_OK, "maximum-length status");
    require(
        output == (int64_t)INT32_MAX * (int64_t)BOUNDED_SUM_MAX_LEN,
        "maximum-length sum"
    );

    const int32_t too_many[BOUNDED_SUM_MAX_LEN + 1] = {0};
    output = -99;
    status = bounded_sum_i32(too_many, BOUNDED_SUM_MAX_LEN + 1, &output);
    require(status == BOUNDED_SUM_LENGTH_ERROR, "oversized status");
    require(output == -99, "oversized call changed output");

    output = -99;
    status = bounded_sum_i32(NULL, 1, &output);
    require(status == BOUNDED_SUM_NULL_POINTER, "null values status");
    require(output == -99, "null values call changed output");

    status = bounded_sum_i32(normal, 3, NULL);
    require(status == BOUNDED_SUM_NULL_POINTER, "null output status");

    if (failures != 0) {
        fprintf(stderr, "c bounded_sum tests: %d failure(s)\n", failures);
        return 1;
    }

    puts("c bounded_sum tests: PASS");
    return 0;
}
