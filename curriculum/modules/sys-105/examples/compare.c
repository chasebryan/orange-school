#include "compare.h"

static int validate(const uint8_t *left, const uint8_t *right, size_t length,
                    const struct sys105_observation *output) {
    if (output == NULL) {
        return 1;
    }
    if (length > SYS105_MAX_BYTES) {
        return 2;
    }
    if (length != 0U && (left == NULL || right == NULL)) {
        return 3;
    }
    return 0;
}

int sys105_early_exit(const uint8_t *left, const uint8_t *right, size_t length,
                      struct sys105_observation *output) {
    struct sys105_observation result = {0U, 1U};
    const int status = validate(left, right, length, output);
    size_t index;

    if (status != 0) {
        return status;
    }
    for (index = 0U; index < length; ++index) {
        result.iterations += 1U;
        if (left[index] != right[index]) {
            result.equal = 0U;
            break;
        }
    }
    *output = result;
    return 0;
}

int sys105_fixed_scan_source(const uint8_t *left, const uint8_t *right,
                             size_t length,
                             struct sys105_observation *output) {
    struct sys105_observation result = {0U, 0U};
    uint8_t difference = 0U;
    const int status = validate(left, right, length, output);
    size_t index;

    if (status != 0) {
        return status;
    }
    for (index = 0U; index < length; ++index) {
        difference = (uint8_t)(difference | (uint8_t)(left[index] ^ right[index]));
        result.iterations += 1U;
    }
    result.equal = (uint8_t)(difference == 0U);
    *output = result;
    return 0;
}
