#![forbid(unsafe_code)]

use civic_model::RuntimeId;

pub fn validate_runtime(id: RuntimeId) -> bool {
    id.0 != 0
}
