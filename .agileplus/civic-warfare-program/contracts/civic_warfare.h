#ifndef CIVIC_WARFARE_H
#define CIVIC_WARFARE_H

#include <stddef.h>
#include <stdint.h>

#ifdef _WIN32
#define CSW_API __declspec(dllexport)
#else
#define CSW_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct CswRuntime CswRuntime;

typedef enum CswResult {
    CSW_OK = 0,
    CSW_BUFFER_TOO_SMALL = 1,
    CSW_INVALID_ARGUMENT = 2,
    CSW_INVALID_HANDLE = 3,
    CSW_INVALID_STATE = 4,
    CSW_ABI_MISMATCH = 5,
    CSW_SCHEMA_MISMATCH = 6,
    CSW_RULES_MISMATCH = 7,
    CSW_REVISION_CONFLICT = 8,
    CSW_CORRUPT_DATA = 9,
    CSW_UNSUPPORTED_VERSION = 10,
    CSW_BUDGET_EXCEEDED = 11,
    CSW_DETERMINISM_FAILURE = 12,
    CSW_INTERNAL_PANIC = 13
} CswResult;

CSW_API uint32_t csw_abi_version(void);
CSW_API CswResult csw_create(const uint8_t *config, size_t config_len, CswRuntime **out_runtime);
CSW_API CswResult csw_load(const uint8_t *save, size_t save_len, CswRuntime **out_runtime);
CSW_API CswResult csw_submit_commands(CswRuntime *runtime, const uint8_t *batch, size_t batch_len);
CSW_API CswResult csw_step(CswRuntime *runtime, const uint8_t *observations, size_t observations_len, uint32_t max_ticks);
CSW_API CswResult csw_poll_into(CswRuntime *runtime, uint8_t *out, size_t out_len, size_t *required_len);
CSW_API CswResult csw_save_into(CswRuntime *runtime, uint8_t *out, size_t out_len, size_t *required_len);
/* Status is serialized into a caller-owned, versioned byte buffer. */
CSW_API CswResult csw_status_into(const CswRuntime *runtime, uint8_t *out, size_t out_len, size_t *required_len);
CSW_API CswResult csw_last_error_into(const CswRuntime *runtime, uint8_t *out, size_t out_len, size_t *required_len);
CSW_API void csw_destroy(CswRuntime **runtime);

#ifdef __cplusplus
}
#endif

#endif
