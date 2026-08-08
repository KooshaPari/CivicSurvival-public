#![deny(unsafe_op_in_unsafe_fn)]

use std::panic::{catch_unwind, AssertUnwindSafe};
use std::ptr;

#[allow(dead_code, non_snake_case, clippy::all)]
mod warfare_generated {
    include!(concat!(env!("OUT_DIR"), "/warfare_generated.rs"));
}

use warfare_generated::civic_survival::warfare::contracts::{
    envelope_buffer_has_identifier, root_as_envelope, RootPayload,
};

pub const ABI_VERSION: u32 = 1;
const SCHEMA_VERSION: u32 = 1;
const SAVE_VERSION: u32 = 1;
const RNG_VERSION: u32 = 1;
const STATUS_LEN: usize = 40;

#[repr(C)]
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum CswResult {
    Ok = 0,
    BufferTooSmall = 1,
    InvalidArgument = 2,
    InvalidHandle = 3,
    InvalidState = 4,
    AbiMismatch = 5,
    SchemaMismatch = 6,
    RulesMismatch = 7,
    RevisionConflict = 8,
    CorruptData = 9,
    UnsupportedVersion = 10,
    BudgetExceeded = 11,
    DeterminismFailure = 12,
    InternalPanic = 13,
}

struct Runtime {
    tick: u64,
    revision: u64,
    last_sequence: u64,
    last_error: Vec<u8>,
}

#[repr(C)]
pub struct CswRuntime {
    _private: [u8; 0],
}

pub fn abi_version() -> u32 {
    ABI_VERSION
}

fn guarded(operation: impl FnOnce() -> CswResult) -> CswResult {
    catch_unwind(AssertUnwindSafe(operation)).unwrap_or(CswResult::InternalPanic)
}

unsafe fn runtime_ref<'a>(runtime: *const CswRuntime) -> Result<&'a Runtime, CswResult> {
    if runtime.is_null() {
        return Err(CswResult::InvalidHandle);
    }
    Ok(unsafe { &*(runtime.cast::<Runtime>()) })
}

fn copy_bytes(out: *mut u8, out_len: usize, required_len: *mut usize, bytes: &[u8]) -> CswResult {
    if required_len.is_null() || (out.is_null() && out_len != 0) {
        return CswResult::InvalidArgument;
    }
    unsafe { *required_len = bytes.len() };
    if out_len < bytes.len() {
        return CswResult::BufferTooSmall;
    }
    if !bytes.is_empty() {
        unsafe { ptr::copy_nonoverlapping(bytes.as_ptr(), out, bytes.len()) };
    }
    CswResult::Ok
}

fn verify_envelope(
    bytes: *const u8,
    len: usize,
    expected_kind: Option<warfare_generated::civic_survival::warfare::contracts::RootPayload>,
) -> CswResult {
    if bytes.is_null() && len != 0 {
        return CswResult::InvalidArgument;
    }
    if len == 0 {
        return if expected_kind.is_some() { CswResult::InvalidArgument } else { CswResult::Ok };
    }
    let bytes = unsafe { std::slice::from_raw_parts(bytes, len) };
    if !envelope_buffer_has_identifier(bytes) {
        return CswResult::SchemaMismatch;
    }
    match root_as_envelope(bytes) {
        Ok(envelope) => {
            if expected_kind.is_some_and(|kind| envelope.payload_type() != kind) {
                CswResult::SchemaMismatch
            } else {
                CswResult::Ok
            }
        }
        Err(_) => CswResult::CorruptData,
    }
}

fn validate_command_batch(bytes: *const u8, len: usize) -> CswResult {
    let bytes = unsafe { std::slice::from_raw_parts(bytes, len) };
    let envelope = match root_as_envelope(bytes) {
        Ok(value) => value,
        Err(_) => return CswResult::CorruptData,
    };
    let Some(batch) = envelope.payload_as_command_batch() else {
        return CswResult::SchemaMismatch;
    };
    if batch.schema_version() != SCHEMA_VERSION {
        return CswResult::UnsupportedVersion;
    }
    CswResult::Ok
}

fn validate_save_envelope(bytes: *const u8, len: usize) -> CswResult {
    let bytes = unsafe { std::slice::from_raw_parts(bytes, len) };
    let envelope = match root_as_envelope(bytes) {
        Ok(value) => value,
        Err(_) => return CswResult::CorruptData,
    };
    let Some(save) = envelope.payload_as_save_envelope() else {
        return CswResult::SchemaMismatch;
    };
    if save.abi_version() != ABI_VERSION {
        return CswResult::AbiMismatch;
    }
    if save.schema_version() != SCHEMA_VERSION
        || save.save_version() != SAVE_VERSION
        || save.rng_version() != RNG_VERSION
    {
        return CswResult::UnsupportedVersion;
    }
    let Some(campaign_id) = save.campaign_id() else { return CswResult::InvalidArgument };
    let Some(rules_hash) = save.rules_manifest_hash() else { return CswResult::InvalidArgument };
    let Some(snapshot) = save.snapshot() else { return CswResult::InvalidArgument };
    let Some(checkpoint) = save.journal_checkpoint() else { return CswResult::InvalidArgument };
    let Some(canonical_hash) = save.canonical_hash() else { return CswResult::InvalidArgument };
    let Some(checksum) = save.checksum() else { return CswResult::InvalidArgument };
    if campaign_id.len() != 16
        || rules_hash.len() != 32
        || snapshot.is_empty()
        || checkpoint.is_empty()
        || canonical_hash.len() != 32
        || checksum.len() != 32
    {
        return CswResult::InvalidArgument;
    }
    CswResult::Ok
}

fn runtime_from_save(bytes: *const u8, len: usize) -> Result<Runtime, CswResult> {
    let slice = unsafe { std::slice::from_raw_parts(bytes, len) };
    let envelope = root_as_envelope(slice).map_err(|_| CswResult::CorruptData)?;
    let save = envelope.payload_as_save_envelope().ok_or(CswResult::SchemaMismatch)?;
    Ok(Runtime {
        tick: save.tick(),
        revision: save.revision(),
        last_sequence: 0,
        last_error: Vec::new(),
    })
}

fn status_bytes(runtime: &Runtime) -> [u8; STATUS_LEN] {
    let mut bytes = [0; STATUS_LEN];
    bytes[0..4].copy_from_slice(&ABI_VERSION.to_le_bytes());
    bytes[4..8].copy_from_slice(&1u32.to_le_bytes());
    bytes[8..12].copy_from_slice(&1u32.to_le_bytes());
    bytes[12..16].copy_from_slice(&0u32.to_le_bytes());
    bytes[16..24].copy_from_slice(&runtime.tick.to_le_bytes());
    bytes[24..32].copy_from_slice(&runtime.revision.to_le_bytes());
    bytes[32..40].copy_from_slice(&runtime.last_sequence.to_le_bytes());
    bytes
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_abi_version() -> u32 {
    ABI_VERSION
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_create(
    config: *const u8,
    config_len: usize,
    out_runtime: *mut *mut CswRuntime,
) -> CswResult {
    guarded(|| {
        if out_runtime.is_null() {
            return CswResult::InvalidArgument;
        }
        unsafe { *out_runtime = ptr::null_mut() };
        if config.is_null() && config_len != 0 {
            return CswResult::InvalidArgument;
        }
        let verification = verify_envelope(config, config_len, None);
        if verification != CswResult::Ok {
            return verification;
        }
        let runtime = Box::new(Runtime { tick: 0, revision: 0, last_sequence: 0, last_error: Vec::new() });
        unsafe { *out_runtime = Box::into_raw(runtime).cast::<CswRuntime>() };
        CswResult::Ok
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_load(
    save: *const u8,
    save_len: usize,
    out_runtime: *mut *mut CswRuntime,
) -> CswResult {
    guarded(|| {
        if out_runtime.is_null() {
            return CswResult::InvalidArgument;
        }
        unsafe { *out_runtime = ptr::null_mut() };
        let expected = RootPayload::SaveEnvelope;
        let verification = verify_envelope(save, save_len, Some(expected));
        if verification != CswResult::Ok {
            return verification;
        }
        let semantic = validate_save_envelope(save, save_len);
        if semantic != CswResult::Ok {
            return semantic;
        }
        let candidate = match runtime_from_save(save, save_len) {
            Ok(value) => Box::new(value),
            Err(error) => return error,
        };
        unsafe { *out_runtime = Box::into_raw(candidate).cast::<CswRuntime>() };
        CswResult::Ok
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_submit_commands(
    runtime: *mut CswRuntime,
    batch: *const u8,
    batch_len: usize,
) -> CswResult {
    guarded(|| unsafe {
        if batch.is_null() && batch_len != 0 {
            return CswResult::InvalidArgument;
        }
        let expected = warfare_generated::civic_survival::warfare::contracts::RootPayload::CommandBatch;
        let verification = verify_envelope(batch, batch_len, Some(expected));
        if verification != CswResult::Ok {
            return verification;
        }
        let semantic = validate_command_batch(batch, batch_len);
        if semantic != CswResult::Ok {
            return semantic;
        }
        runtime_ref(runtime.cast_const()).map_or_else(|error| error, |value| {
            let _ = value;
            CswResult::Ok
        })
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_step(
    runtime: *mut CswRuntime,
    observations: *const u8,
    observations_len: usize,
    max_ticks: u32,
) -> CswResult {
    guarded(|| unsafe {
        if observations.is_null() && observations_len != 0 {
            return CswResult::InvalidArgument;
        }
        runtime_ref(runtime.cast_const()).map_or_else(|error| error, |_| {
            let runtime = &mut *(runtime.cast::<Runtime>());
            runtime.tick = runtime.tick.saturating_add(u64::from(max_ticks));
            runtime.revision = runtime.revision.saturating_add(1);
            CswResult::Ok
        })
    })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_poll_into(
    runtime: *mut CswRuntime,
    out: *mut u8,
    out_len: usize,
    required_len: *mut usize,
) -> CswResult {
    guarded(|| unsafe { runtime_ref(runtime.cast_const()).map_or_else(|error| error, |_| copy_bytes(out, out_len, required_len, &[])) })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_save_into(
    runtime: *mut CswRuntime,
    out: *mut u8,
    out_len: usize,
    required_len: *mut usize,
) -> CswResult {
    guarded(|| unsafe { runtime_ref(runtime.cast_const()).map_or_else(|error| error, |_| copy_bytes(out, out_len, required_len, &[])) })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_destroy(runtime: *mut CswRuntime) {
    let _ = catch_unwind(AssertUnwindSafe(|| {
        if !runtime.is_null() {
            unsafe { drop(Box::from_raw(runtime.cast::<Runtime>())) };
        }
    }));
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_status_into(
    runtime: *const CswRuntime,
    out: *mut u8,
    out_len: usize,
    required_len: *mut usize,
) -> CswResult {
    guarded(|| unsafe { runtime_ref(runtime).map_or_else(|error| error, |value| copy_bytes(out, out_len, required_len, &status_bytes(value))) })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_last_error_into(
    runtime: *const CswRuntime,
    out: *mut u8,
    out_len: usize,
    required_len: *mut usize,
) -> CswResult {
    guarded(|| unsafe { runtime_ref(runtime).map_or_else(|error| error, |value| copy_bytes(out, out_len, required_len, &value.last_error)) })
}

#[cfg(test)]
mod tests {
    use super::*;
    use flatbuffers::FlatBufferBuilder;
    use warfare_generated::civic_survival::warfare::contracts::{
        CommandBatch, CommandBatchArgs, Envelope, EnvelopeArgs, SaveEnvelope, SaveEnvelopeArgs,
    };

    fn valid_envelope() -> Vec<u8> {
        let mut builder = FlatBufferBuilder::new();
        let envelope = Envelope::create(&mut builder, &EnvelopeArgs {
            payload_type: RootPayload::NONE,
            payload: None,
        });
        builder.finish(envelope, Some("CSWP"));
        builder.finished_data().to_vec()
    }

    fn valid_command_batch() -> Vec<u8> {
        let mut builder = FlatBufferBuilder::new();
        let batch = CommandBatch::create(&mut builder, &CommandBatchArgs {
            schema_version: SCHEMA_VERSION,
            commands: None,
        });
        let envelope = Envelope::create(&mut builder, &EnvelopeArgs {
            payload_type: RootPayload::CommandBatch,
            payload: Some(batch.as_union_value()),
        });
        builder.finish(envelope, Some("CSWP"));
        builder.finished_data().to_vec()
    }

    fn valid_save_envelope() -> Vec<u8> {
        let mut builder = FlatBufferBuilder::new();
        let campaign_id = builder.create_vector(&[0x11u8; 16]);
        let rules_hash = builder.create_vector(&[0x22u8; 32]);
        let snapshot = builder.create_vector(&[0x33u8, 0x44]);
        let checkpoint = builder.create_vector(&[0x55u8]);
        let canonical_hash = builder.create_vector(&[0x66u8; 32]);
        let checksum = builder.create_vector(&[0x77u8; 32]);
        let save = SaveEnvelope::create(&mut builder, &SaveEnvelopeArgs {
            abi_version: ABI_VERSION,
            schema_version: SCHEMA_VERSION,
            save_version: SAVE_VERSION,
            rng_version: RNG_VERSION,
            campaign_id: Some(campaign_id),
            rules_manifest_hash: Some(rules_hash),
            tick: 7,
            revision: 9,
            snapshot: Some(snapshot),
            journal_checkpoint: Some(checkpoint),
            canonical_hash: Some(canonical_hash),
            checksum: Some(checksum),
        });
        let envelope = Envelope::create(&mut builder, &EnvelopeArgs {
            payload_type: RootPayload::SaveEnvelope,
            payload: Some(save.as_union_value()),
        });
        builder.finish(envelope, Some("CSWP"));
        builder.finished_data().to_vec()
    }

    #[test]
    fn create_status_and_destroy_round_trip() {
        let mut handle = ptr::null_mut();
        assert_eq!(csw_create(ptr::null(), 0, &mut handle), CswResult::Ok);
        assert!(!handle.is_null());
        let mut required = 0;
        assert_eq!(csw_status_into(handle, ptr::null_mut(), 0, &mut required), CswResult::BufferTooSmall);
        assert_eq!(required, STATUS_LEN);
        let mut output = [0; STATUS_LEN];
        assert_eq!(csw_status_into(handle, output.as_mut_ptr(), output.len(), &mut required), CswResult::Ok);
        assert_eq!(required, STATUS_LEN);
        let mut short = [0xA5; 2];
        assert_eq!(csw_status_into(handle, short.as_mut_ptr(), short.len(), &mut required), CswResult::BufferTooSmall);
        assert_eq!(short, [0xA5; 2]);
        csw_destroy(handle);
    }

    #[test]
    fn invalid_handles_and_output_contracts_fail_closed() {
        let mut required = 0;
        assert_eq!(csw_status_into(ptr::null(), ptr::null_mut(), 0, &mut required), CswResult::InvalidHandle);
        assert_eq!(csw_create(ptr::null(), 1, ptr::null_mut()), CswResult::InvalidArgument);
        assert_eq!(csw_status_into(ptr::null(), ptr::null_mut(), 0, ptr::null_mut()), CswResult::InvalidHandle);
    }

    #[test]
    fn step_and_empty_output_calls_are_bounded() {
        let mut handle = ptr::null_mut();
        assert_eq!(csw_create(ptr::null(), 0, &mut handle), CswResult::Ok);
        assert_eq!(csw_step(handle, ptr::null(), 0, 3), CswResult::Ok);
        let mut status = [0; STATUS_LEN];
        let mut required = 0;
        assert_eq!(csw_status_into(handle, status.as_mut_ptr(), status.len(), &mut required), CswResult::Ok);
        assert_eq!(u64::from_le_bytes(status[16..24].try_into().unwrap()), 3);
        assert_eq!(csw_poll_into(handle, ptr::null_mut(), 0, &mut required), CswResult::Ok);
        assert_eq!(required, 0);
        assert_eq!(csw_save_into(handle, ptr::null_mut(), 0, &mut required), CswResult::Ok);
        csw_destroy(handle);
    }

    #[test]
    fn inbound_envelopes_are_verified_before_acceptance() {
        let valid = valid_envelope();
        let mut handle = ptr::null_mut();
        assert_eq!(csw_create(valid.as_ptr(), valid.len(), &mut handle), CswResult::Ok);
        assert_eq!(csw_submit_commands(handle, valid.as_ptr(), valid.len()), CswResult::SchemaMismatch);

        let mut truncated = valid.clone();
        truncated.pop();
        assert_eq!(csw_submit_commands(handle, truncated.as_ptr(), truncated.len()), CswResult::CorruptData);

        let mut wrong_identifier = valid;
        wrong_identifier[4..8].copy_from_slice(b"NOPE");
        let mut replacement = ptr::null_mut();
        assert_eq!(csw_load(wrong_identifier.as_ptr(), wrong_identifier.len(), &mut replacement), CswResult::SchemaMismatch);
        assert_eq!(csw_load(ptr::null(), 0, &mut replacement), CswResult::InvalidArgument);
        csw_destroy(handle);
    }

    #[test]
    fn typed_vectors_are_accepted_and_load_is_transactional() {
        let command_batch = valid_command_batch();
        let mut handle = ptr::null_mut();
        assert_eq!(csw_create(ptr::null(), 0, &mut handle), CswResult::Ok);
        assert_eq!(csw_submit_commands(handle, command_batch.as_ptr(), command_batch.len()), CswResult::Ok);

        let save = valid_save_envelope();
        let mut loaded = ptr::null_mut();
        assert_eq!(csw_load(save.as_ptr(), save.len(), &mut loaded), CswResult::Ok);
        assert!(!loaded.is_null());
        let mut status = [0; STATUS_LEN];
        let mut required = 0;
        assert_eq!(csw_status_into(loaded, status.as_mut_ptr(), status.len(), &mut required), CswResult::Ok);
        assert_eq!(u64::from_le_bytes(status[16..24].try_into().unwrap()), 7);
        assert_eq!(u64::from_le_bytes(status[24..32].try_into().unwrap()), 9);
        csw_destroy(loaded);
        csw_destroy(handle);
    }
}
