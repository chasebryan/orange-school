#include "owned_buffer.h"

#include <stdlib.h>
#include <string.h>

static int sys102_buffer_shape_is_valid(const struct sys102_buffer *buffer) {
    if (buffer == NULL) {
        return 0;
    }
    if (buffer->len > SYS102_MAX_BYTES) {
        return 0;
    }
    if (buffer->len == 0) {
        return buffer->data == NULL;
    }
    return buffer->data != NULL;
}

int sys102_buffer_clone(
    const uint8_t *source,
    size_t len,
    struct sys102_buffer *out
) {
    uint8_t *copy;

    if (out == NULL) {
        return SYS102_NULL_POINTER;
    }
    if (!sys102_buffer_shape_is_valid(out) || out->data != NULL || out->len != 0) {
        return SYS102_STATE_ERROR;
    }
    if (len > SYS102_MAX_BYTES) {
        return SYS102_LENGTH_ERROR;
    }
    if (len > 0 && source == NULL) {
        return SYS102_NULL_POINTER;
    }
    if (len == 0) {
        return SYS102_OK;
    }

    copy = malloc(len);
    if (copy == NULL) {
        return SYS102_ALLOCATION_ERROR;
    }
    memcpy(copy, source, len);
    out->data = copy;
    out->len = len;
    return SYS102_OK;
}

int sys102_buffer_sum(
    const struct sys102_buffer *buffer,
    uint64_t *out_sum
) {
    uint64_t sum = 0;
    size_t index;

    if (buffer == NULL || out_sum == NULL) {
        return SYS102_NULL_POINTER;
    }
    if (!sys102_buffer_shape_is_valid(buffer)) {
        return SYS102_STATE_ERROR;
    }

    for (index = 0; index < buffer->len; ++index) {
        sum += (uint64_t)buffer->data[index];
    }
    *out_sum = sum;
    return SYS102_OK;
}

int sys102_buffer_wipe(struct sys102_buffer *buffer) {
    volatile uint8_t *cursor;
    size_t index;

    if (buffer == NULL) {
        return SYS102_NULL_POINTER;
    }
    if (!sys102_buffer_shape_is_valid(buffer)) {
        return SYS102_STATE_ERROR;
    }

    cursor = (volatile uint8_t *)buffer->data;
    for (index = 0; index < buffer->len; ++index) {
        cursor[index] = 0;
    }
    return SYS102_OK;
}

int sys102_buffer_destroy(struct sys102_buffer *buffer) {
    int status;

    if (buffer == NULL) {
        return SYS102_NULL_POINTER;
    }
    if (!sys102_buffer_shape_is_valid(buffer)) {
        return SYS102_STATE_ERROR;
    }

    status = sys102_buffer_wipe(buffer);
    if (status != SYS102_OK) {
        return status;
    }
    free(buffer->data);
    buffer->data = NULL;
    buffer->len = 0;
    return SYS102_OK;
}
