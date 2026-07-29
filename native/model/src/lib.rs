#![forbid(unsafe_code)]

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct RuntimeId(pub u64);

#[cfg(test)]
mod tests {
    use super::RuntimeId;

    #[test]
    fn runtime_ids_are_copyable_and_explicit() {
        assert_eq!(RuntimeId(7), RuntimeId(7));
    }
}
