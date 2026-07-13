#include "abi_contract.h"

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static int failures = 0;

static void require(int condition, const char *message)
{
    if (!condition) {
        (void)fprintf(stderr, "C check failed: %s\n", message);
        ++failures;
    }
}

static void check_normal_and_endpoints(void)
{
    const uint8_t payload[] = {UINT8_C(2), UINT8_C(4), UINT8_C(8)};
    const sys103_request request = {
        UINT32_C(100), UINT16_C(2), UINT16_C(3)
    };
    const sys103_request empty = {
        UINT32_C(7), UINT16_C(0), UINT16_C(0)
    };
    uint8_t maximum_payload[SYS103_MAX_PAYLOAD];
    const sys103_request maximum = {
        UINT32_MAX, UINT16_C(3), (uint16_t)SYS103_MAX_PAYLOAD
    };
    uint32_t output = UINT32_C(0);
    uint32_t index;

    require(
        sys103_checksum(&request, payload, UINT32_C(3), &output) ==
            SYS103_STATUS_OK,
        "normal call status"
    );
    require(output == UINT32_C(3775703), "normal call result");

    output = UINT32_C(99);
    require(
        sys103_checksum(&empty, NULL, UINT32_C(0), &output) ==
            SYS103_STATUS_OK,
        "empty endpoint status"
    );
    require(output == UINT32_C(7), "empty endpoint result");

    for (index = UINT32_C(0); index < SYS103_MAX_PAYLOAD; ++index) {
        maximum_payload[index] = UINT8_MAX;
    }
    require(
        sys103_checksum(
            &maximum, maximum_payload, SYS103_MAX_PAYLOAD, &output
        ) == SYS103_STATUS_OK,
        "maximum endpoint status"
    );
}

static void check_invalid_contracts(void)
{
    const uint8_t payload[] = {UINT8_C(9)};
    const sys103_request one = {
        UINT32_C(1), UINT16_C(1), UINT16_C(1)
    };
    const sys103_request wrong_length = {
        UINT32_C(1), UINT16_C(1), UINT16_C(2)
    };
    const sys103_request wrong_kind = {
        UINT32_C(1), UINT16_C(4), UINT16_C(1)
    };
    uint32_t output = UINT32_C(0xdecafbad);

    require(
        sys103_checksum(NULL, payload, UINT32_C(1), &output) ==
            SYS103_STATUS_NULL,
        "null request status"
    );
    require(output == UINT32_C(0xdecafbad), "null request preserves output");
    require(
        sys103_checksum(&one, payload, UINT32_C(1), NULL) ==
            SYS103_STATUS_NULL,
        "null output status"
    );
    require(
        sys103_checksum(&one, payload, UINT32_C(17), &output) ==
            SYS103_STATUS_LENGTH,
        "over-limit length status"
    );
    require(output == UINT32_C(0xdecafbad), "length error preserves output");
    require(
        sys103_checksum(&wrong_length, payload, UINT32_C(1), &output) ==
            SYS103_STATUS_LENGTH,
        "mismatched length status"
    );
    require(
        sys103_checksum(&wrong_kind, payload, UINT32_C(1), &output) ==
            SYS103_STATUS_KIND,
        "invalid kind status"
    );
    require(
        sys103_checksum(&one, NULL, UINT32_C(1), &output) ==
            SYS103_STATUS_NULL,
        "null nonempty payload status"
    );
    require(output == UINT32_C(0xdecafbad), "all errors preserve output");
}

static void check_layout_observations(void)
{
    require(sys103_request_size() >= UINT32_C(8), "request size lower bound");
    require(sys103_request_align() >= UINT32_C(1), "request alignment");
    require(
        sys103_request_request_id_offset() == UINT32_C(0),
        "first request field offset"
    );
    require(
        sys103_request_kind_offset() >= UINT32_C(4),
        "request kind follows request id"
    );
    require(
        sys103_request_payload_len_offset() > sys103_request_kind_offset(),
        "request payload length follows kind"
    );

    require(sys103_demo_size() >= UINT32_C(7), "demo size lower bound");
    require(sys103_demo_align() >= UINT32_C(1), "demo alignment");
    require(sys103_demo_tag_offset() == UINT32_C(0), "first demo field offset");
    require(
        sys103_demo_value_offset() > sys103_demo_tag_offset(),
        "demo value follows tag"
    );
    require(
        sys103_demo_code_offset() > sys103_demo_value_offset(),
        "demo code follows value"
    );
    require(strcmp(sys103_library_tag, "sys-103-c17") == 0, "library tag");
}

int main(void)
{
    check_normal_and_endpoints();
    check_invalid_contracts();
    check_layout_observations();
    if (failures != 0) {
        return 1;
    }
    (void)printf(
        "c ABI tests: PASS; request size=%u align=%u; demo size=%u align=%u\n",
        (unsigned int)sys103_request_size(),
        (unsigned int)sys103_request_align(),
        (unsigned int)sys103_demo_size(),
        (unsigned int)sys103_demo_align()
    );
    return 0;
}
