#![forbid(unsafe_code)]

pub fn smoke() -> bool {
    civic_application::open(civic_model::RuntimeId(1)).is_ok()
}

#[cfg(test)]
mod tests {
    #[test]
    fn empty_headless_runtime_smoke_is_available() {
        assert!(super::smoke());
    }
}
