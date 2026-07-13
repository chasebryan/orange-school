#include "compare.h"

#include <inttypes.h>
#include <stdio.h>
#include <string.h>

typedef int (*compare_fn)(const uint8_t *, const uint8_t *, size_t,
                          struct sys105_observation *);

static int observe(const char *label, compare_fn function, const uint8_t *left,
                   const uint8_t *right) {
    struct sys105_observation observation = {99U, 99U};
    const int status = function(left, right, SYS105_MAX_BYTES, &observation);
    if (status != 0) {
        return 1;
    }
    if (printf("%s iterations=%" PRIu32 " equal=%u\n", label, observation.iterations,
               (unsigned int)observation.equal) < 0) {
        return 1;
    }
    return 0;
}

int main(void) {
    uint8_t reference[SYS105_MAX_BYTES];
    uint8_t prefix_difference[SYS105_MAX_BYTES];
    uint8_t suffix_difference[SYS105_MAX_BYTES];
    struct sys105_observation unchanged = {71U, 1U};

    memset(reference, 0x5a, sizeof reference);
    memcpy(prefix_difference, reference, sizeof reference);
    memcpy(suffix_difference, reference, sizeof reference);
    prefix_difference[0] ^= 1U;
    suffix_difference[SYS105_MAX_BYTES - 1U] ^= 1U;

    if (observe("leaky-prefix", sys105_early_exit, reference,
                prefix_difference) != 0 ||
        observe("leaky-suffix", sys105_early_exit, reference,
                suffix_difference) != 0 ||
        observe("control-prefix", sys105_fixed_scan_source, reference,
                prefix_difference) != 0 ||
        observe("control-suffix", sys105_fixed_scan_source, reference,
                suffix_difference) != 0 ||
        observe("control-equal", sys105_fixed_scan_source, reference,
                reference) != 0) {
        return 1;
    }

    if (sys105_fixed_scan_source(reference, reference, SYS105_MAX_BYTES + 1U,
                                 &unchanged) != 2 ||
        unchanged.iterations != 71U || unchanged.equal != 1U) {
        return 1;
    }
    return 0;
}
