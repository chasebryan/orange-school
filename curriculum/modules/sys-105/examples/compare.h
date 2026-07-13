#ifndef SYS105_COMPARE_H
#define SYS105_COMPARE_H

#include <stddef.h>
#include <stdint.h>

#define SYS105_MAX_BYTES ((size_t)32)

struct sys105_observation {
    uint32_t iterations;
    uint8_t equal;
};

/*
 * These functions are teaching fixtures, not security primitives.  The
 * iteration counter deliberately changes the generated artifact and makes no
 * timing or constant-time guarantee.
 */
int sys105_early_exit(const uint8_t *left, const uint8_t *right, size_t length,
                      struct sys105_observation *output);
int sys105_fixed_scan_source(const uint8_t *left, const uint8_t *right,
                             size_t length,
                             struct sys105_observation *output);

#endif
