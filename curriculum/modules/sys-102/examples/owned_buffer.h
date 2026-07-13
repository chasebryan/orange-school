#ifndef SYS102_OWNED_BUFFER_H
#define SYS102_OWNED_BUFFER_H

#include <stddef.h>
#include <stdint.h>

#define SYS102_MAX_BYTES ((size_t)32)

enum sys102_status {
    SYS102_OK = 0,
    SYS102_NULL_POINTER = 1,
    SYS102_LENGTH_ERROR = 2,
    SYS102_STATE_ERROR = 3,
    SYS102_ALLOCATION_ERROR = 4
};

/*
 * An initialized empty value is {NULL, 0}. A successful clone transfers
 * ownership of one malloc allocation to this value. Exactly one owner may
 * later pass that value to sys102_buffer_destroy. The data pointer must not be
 * freed, offset, replaced, or retained by another owner in the meantime.
 */
struct sys102_buffer {
    uint8_t *data;
    size_t len;
};

#define SYS102_BUFFER_INIT {NULL, (size_t)0}

/*
 * Clone source[0..len) into a new allocation and transfer its ownership to
 * *out. The caller provides an initialized empty out value. For len > 0,
 * source identifies len readable uint8_t objects whose lifetimes cover the
 * call. The source range and out object do not overlap. No source pointer is
 * retained. On failure, *out is unchanged.
 */
int sys102_buffer_clone(
    const uint8_t *source,
    size_t len,
    struct sys102_buffer *out
);

/*
 * Sum the owned bytes. The input allocation remains owned by buffer and is
 * not mutated or retained. On failure, *out_sum is unchanged.
 */
int sys102_buffer_sum(
    const struct sys102_buffer *buffer,
    uint64_t *out_sum
);

/*
 * Perform volatile-qualified zero assignments to each byte in this selected
 * live allocation. Success plus readback establishes only the tested
 * language/toolchain observation for this allocation. It does not establish
 * erasure of source copies, compiler temporaries, registers, caches, swap,
 * crash dumps, backups, or storage media.
 */
int sys102_buffer_wipe(struct sys102_buffer *buffer);

/*
 * Wipe the selected allocation, pass its original base pointer to free, and
 * reset *buffer to {NULL, 0}. Success consumes that allocation ownership.
 * Calling destroy again on the reset empty value is valid. A fabricated,
 * interior, stale, already-freed, or otherwise invalid non-null pointer is
 * outside this API contract; C cannot validate such provenance or extent.
 */
int sys102_buffer_destroy(struct sys102_buffer *buffer);

#endif
