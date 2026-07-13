#include "abi_contract.h"

#include <stddef.h>

const char sys103_library_tag[] = "sys-103-c17";

/* Internal linkage keeps this helper private to this translation unit. */
static uint32_t fold_byte(uint32_t state, uint8_t byte)
{
    return state * UINT32_C(33) + (uint32_t)byte;
}

int32_t sys103_checksum(
    const sys103_request *request,
    const uint8_t *payload,
    uint32_t payload_len,
    uint32_t *out_checksum
)
{
    uint32_t state;
    uint32_t index;

    if (out_checksum == NULL || request == NULL) {
        return SYS103_STATUS_NULL;
    }
    if (payload_len > SYS103_MAX_PAYLOAD ||
        payload_len != (uint32_t)request->payload_len) {
        return SYS103_STATUS_LENGTH;
    }
    if (request->kind > UINT16_C(3)) {
        return SYS103_STATUS_KIND;
    }
    if (payload_len != UINT32_C(0) && payload == NULL) {
        return SYS103_STATUS_NULL;
    }

    /* uint32_t arithmetic is deliberately modulo 2^32. */
    state = request->request_id + (uint32_t)request->kind + payload_len;
    for (index = UINT32_C(0); index < payload_len; ++index) {
        state = fold_byte(state, payload[index]);
    }
    *out_checksum = state;
    return SYS103_STATUS_OK;
}
