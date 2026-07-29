#![forbid(unsafe_code)]

use civic_model::RuntimeId;

pub fn open(id: RuntimeId) -> Result<RuntimeId, &'static str> {
    civic_rules::validate_runtime(id).then_some(id).ok_or("invalid runtime id")
}
