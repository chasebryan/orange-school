#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

enum {
    SYS104_OK = 0,
    SYS104_NULL = 1,
    SYS104_LENGTH = 2,
    SYS104_MAX_ITEMS = 32
};

/*
 * This is the portable scalar implementation. The build and inspection
 * record, not this source file, identifies its target ABI and object format.
 */
static int sys104_add_u32(
    const uint32_t *left,
    const uint32_t *right,
    uint32_t *output,
    size_t length
)
{
    size_t index;

    if (length > SYS104_MAX_ITEMS) {
        return SYS104_LENGTH;
    }
    if (length == 0U) {
        return SYS104_OK;
    }
    if (left == NULL || right == NULL || output == NULL) {
        return SYS104_NULL;
    }
    for (index = 0U; index < length; ++index) {
        output[index] = left[index] + right[index];
    }
    return SYS104_OK;
}

static int require(int condition, const char *message)
{
    if (!condition) {
        (void)fprintf(stderr, "sys-104 C baseline: FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

int main(void)
{
    const uint32_t left[] = {0U, UINT32_MAX, 10U, 20U};
    const uint32_t right[] = {0U, 1U, 30U, 40U};
    uint32_t output[] = {99U, 99U, 99U, 99U};
    uint32_t maximum_left[SYS104_MAX_ITEMS] = {0U};
    uint32_t maximum_right[SYS104_MAX_ITEMS] = {0U};
    uint32_t maximum_output[SYS104_MAX_ITEMS] = {0U};
    size_t index;

    if (!require(
            sys104_add_u32(left, right, output, 4U) == SYS104_OK,
            "normal input was rejected"
        ) ||
        !require(
            output[0] == 0U && output[1] == 0U &&
                output[2] == 40U && output[3] == 60U,
            "lane addition semantics changed"
        ) ||
        !require(
            sys104_add_u32(NULL, NULL, NULL, 0U) == SYS104_OK,
            "empty endpoint was rejected"
        ) ||
        !require(
            sys104_add_u32(NULL, right, output, 1U) == SYS104_NULL,
            "null input was accepted"
        ) ||
        !require(
            sys104_add_u32(left, right, output, SYS104_MAX_ITEMS + 1U) ==
                SYS104_LENGTH,
            "over-budget input was accepted"
        )) {
        return 1;
    }

    for (index = 0U; index < SYS104_MAX_ITEMS; ++index) {
        maximum_left[index] = (uint32_t)index;
        maximum_right[index] = UINT32_MAX - (uint32_t)index;
    }
    if (!require(
            sys104_add_u32(
                maximum_left,
                maximum_right,
                maximum_output,
                SYS104_MAX_ITEMS
            ) == SYS104_OK,
            "maximum input was rejected"
        )) {
        return 1;
    }
    for (index = 0U; index < SYS104_MAX_ITEMS; ++index) {
        if (!require(maximum_output[index] == UINT32_MAX, "maximum result changed")) {
            return 1;
        }
    }

    (void)puts("sys-104 C baseline: PASS");
    return 0;
}
