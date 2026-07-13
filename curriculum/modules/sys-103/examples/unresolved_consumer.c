#include <stdint.h>

extern uint32_t sys103_missing_definition(uint32_t value);

int main(void)
{
    return sys103_missing_definition(UINT32_C(7)) == UINT32_C(7) ? 0 : 1;
}
