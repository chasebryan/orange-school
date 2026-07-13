#ifndef SYS103_ABI_CONTRACT_H
#define SYS103_ABI_CONTRACT_H

#include <stdint.h>

#define SYS103_MAX_PAYLOAD UINT32_C(16)

#define SYS103_STATUS_OK INT32_C(0)
#define SYS103_STATUS_NULL INT32_C(1)
#define SYS103_STATUS_LENGTH INT32_C(2)
#define SYS103_STATUS_KIND INT32_C(3)

/*
 * Only exact-width integer fields cross this teaching interface. Compilation
 * itself establishes that this C17 implementation provides these optional
 * stdint.h typedefs. Layout is still a target ABI fact, so the companion
 * probe reports rather than assumes size, alignment, and offsets.
 */
typedef struct sys103_request {
    uint32_t request_id;
    uint16_t kind;
    uint16_t payload_len;
} sys103_request;

/* The field order makes target padding visible in the layout probe. */
typedef struct sys103_layout_demo {
    uint8_t tag;
    uint32_t value;
    uint16_t code;
} sys103_layout_demo;

extern const char sys103_library_tag[];

/*
 * Caller contract:
 * - out_checksum designates one live, aligned, writable uint32_t object;
 * - request designates one live, aligned, readable sys103_request object;
 * - payload_len is at most SYS103_MAX_PAYLOAD and equals request->payload_len;
 * - request->kind is in the closed interval 0..3;
 * - when payload_len is nonzero, payload designates that many readable bytes;
 * - input storage does not overlap out_checksum; and
 * - all designated storage remains valid for the synchronous call.
 *
 * The function retains no pointer, invokes no callback, and never writes the
 * output on error. C code does not unwind through this boundary.
 */
int32_t sys103_checksum(
    const sys103_request *request,
    const uint8_t *payload,
    uint32_t payload_len,
    uint32_t *out_checksum
);

uint32_t sys103_request_size(void);
uint32_t sys103_request_align(void);
uint32_t sys103_request_request_id_offset(void);
uint32_t sys103_request_kind_offset(void);
uint32_t sys103_request_payload_len_offset(void);

uint32_t sys103_demo_size(void);
uint32_t sys103_demo_align(void);
uint32_t sys103_demo_tag_offset(void);
uint32_t sys103_demo_value_offset(void);
uint32_t sys103_demo_code_offset(void);

#endif
