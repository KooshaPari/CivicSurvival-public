#![forbid(unsafe_code)]

pub const ABI_VERSION: u32 = 1;

pub fn abi_version() -> u32 {
    ABI_VERSION
}
