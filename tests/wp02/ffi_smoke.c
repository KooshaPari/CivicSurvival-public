#include <stddef.h>
#include <stdint.h>

#include "civic_warfare.h"

int main(void) {
    if (csw_abi_version() != 1u) {
        return 1;
    }

    CswRuntime *runtime = NULL;
    if (csw_create(NULL, 0u, &runtime) != CSW_OK || runtime == NULL) {
        return 2;
    }

    uint8_t status[40] = {0};
    size_t required = 0u;
    if (csw_status_into(runtime, status, sizeof(status), &required) != CSW_OK ||
        required != sizeof(status)) {
        csw_destroy(runtime);
        return 3;
    }

    csw_destroy(runtime);
    return 0;
}
