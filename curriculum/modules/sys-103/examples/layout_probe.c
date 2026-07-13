#include "abi_contract.h"

#include <stddef.h>

_Static_assert(
    sizeof(sys103_request) <= UINT32_MAX,
    "request layout measurements must fit uint32_t"
);
_Static_assert(
    sizeof(sys103_layout_demo) <= UINT32_MAX,
    "demo layout measurements must fit uint32_t"
);

/*
 * These functions expose observations from this C compiler and target. They
 * are evidence about the built artifacts, not universal C layout constants.
 */
uint32_t sys103_request_size(void)
{
    return (uint32_t)sizeof(sys103_request);
}

uint32_t sys103_request_align(void)
{
    return (uint32_t)_Alignof(sys103_request);
}

uint32_t sys103_request_request_id_offset(void)
{
    return (uint32_t)offsetof(sys103_request, request_id);
}

uint32_t sys103_request_kind_offset(void)
{
    return (uint32_t)offsetof(sys103_request, kind);
}

uint32_t sys103_request_payload_len_offset(void)
{
    return (uint32_t)offsetof(sys103_request, payload_len);
}

uint32_t sys103_demo_size(void)
{
    return (uint32_t)sizeof(sys103_layout_demo);
}

uint32_t sys103_demo_align(void)
{
    return (uint32_t)_Alignof(sys103_layout_demo);
}

uint32_t sys103_demo_tag_offset(void)
{
    return (uint32_t)offsetof(sys103_layout_demo, tag);
}

uint32_t sys103_demo_value_offset(void)
{
    return (uint32_t)offsetof(sys103_layout_demo, value);
}

uint32_t sys103_demo_code_offset(void)
{
    return (uint32_t)offsetof(sys103_layout_demo, code);
}
