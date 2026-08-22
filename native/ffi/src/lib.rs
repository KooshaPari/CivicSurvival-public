#![deny(unsafe_op_in_unsafe_fn)]

mod command;
mod projection;

use std::collections::BTreeSet;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::ptr;

#[allow(dead_code, non_snake_case, clippy::all)]
mod warfare_generated {
    include!(concat!(env!("OUT_DIR"), "/warfare_generated.rs"));
}

use warfare_generated::civic_survival::warfare::contracts::{
    envelope_buffer_has_identifier, root_as_envelope, CommandKind, DecisionCode, Envelope, EnvelopeArgs, RootPayload,
    SaveEnvelope, SaveEnvelopeArgs,
};
use projection::{DecisionRecord, projection_bytes};

pub const ABI_VERSION: u32 = 1;
const SCHEMA_VERSION: u32 = 1;
const SAVE_VERSION: u32 = 1;
const RNG_VERSION: u32 = 1;
const STATUS_LEN: usize = 40;
const ID_LEN: usize = 16;
const MAX_COMMANDS_PER_BATCH: usize = 256;
const MAX_ACCEPTED_COMMAND_IDS: usize = 4096;
const JOURNAL_MAGIC: &[u8; 4] = b"CSWH";
const JOURNAL_VERSION: u32 = 1;

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
    initialized: bool,
    tick: u64,
    revision: u64,
    last_sequence: u64,
    last_error: Vec<u8>,
    campaign_id: [u8; 16],
    rules_manifest_hash: [u8; 32],
    snapshot: Vec<u8>,
    journal_checkpoint: Vec<u8>,
    canonical_hash: [u8; 32],
    checksum: [u8; 32],
    accepted_command_ids: BTreeSet<[u8; ID_LEN]>,
    last_decisions: Vec<DecisionRecord>,
    projection_base_revision: u64,
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
    let Some(canonical_hash_vector) = save.canonical_hash() else { return CswResult::InvalidArgument };
    let Some(checksum_vector) = save.checksum() else { return CswResult::InvalidArgument };
    if campaign_id.len() != 16
        || rules_hash.len() != 32
        || snapshot.is_empty()
        || checkpoint.is_empty()
        || canonical_hash_vector.len() != 32
        || checksum_vector.len() != 32
    {
        return CswResult::InvalidArgument;
    }
    let expected_canonical = canonical_hash(
        campaign_id.bytes().to_vec().as_slice(),
        rules_hash.bytes().to_vec().as_slice(),
        save.tick(),
        save.revision(),
        snapshot.bytes().to_vec().as_slice(),
        checkpoint.bytes().to_vec().as_slice(),
    );
    let expected_checksum = checksum_hash(&expected_canonical);
    if canonical_hash_vector.bytes().to_vec() != expected_canonical
        || checksum_vector.bytes().to_vec() != expected_checksum
    {
        return CswResult::CorruptData;
    }
    CswResult::Ok
}

fn canonical_material(
    campaign_id: &[u8],
    rules_hash: &[u8],
    tick: u64,
    revision: u64,
    snapshot: &[u8],
    checkpoint: &[u8],
) -> Vec<u8> {
    let mut material = Vec::with_capacity(128 + snapshot.len() + checkpoint.len());
    material.extend_from_slice(b"CIVIC-SURVIVAL/CANONICAL-STATE\0");
    material.extend_from_slice(&1u32.to_le_bytes());
    material.extend_from_slice(&ABI_VERSION.to_le_bytes());
    material.extend_from_slice(&SCHEMA_VERSION.to_le_bytes());
    material.extend_from_slice(&SAVE_VERSION.to_le_bytes());
    material.extend_from_slice(&RNG_VERSION.to_le_bytes());
    material.extend_from_slice(&(campaign_id.len() as u32).to_le_bytes());
    material.extend_from_slice(campaign_id);
    material.extend_from_slice(&(rules_hash.len() as u32).to_le_bytes());
    material.extend_from_slice(rules_hash);
    material.extend_from_slice(&tick.to_le_bytes());
    material.extend_from_slice(&revision.to_le_bytes());
    material.extend_from_slice(&(snapshot.len() as u32).to_le_bytes());
    material.extend_from_slice(snapshot);
    material.extend_from_slice(&(checkpoint.len() as u32).to_le_bytes());
    material.extend_from_slice(checkpoint);
    material
}

fn canonical_hash(campaign_id: &[u8], rules_hash: &[u8], tick: u64, revision: u64, snapshot: &[u8], checkpoint: &[u8]) -> [u8; 32] {
    *blake3::hash(&canonical_material(campaign_id, rules_hash, tick, revision, snapshot, checkpoint)).as_bytes()
}

fn checksum_hash(canonical: &[u8; 32]) -> [u8; 32] {
    let mut material = Vec::with_capacity(64);
    material.extend_from_slice(b"CIVIC-SURVIVAL/SAVE-INTEGRITY\0");
    material.extend_from_slice(&1u32.to_le_bytes());
    material.extend_from_slice(canonical);
    *blake3::hash(&material).as_bytes()
}

fn encode_command_history(ids: &BTreeSet<[u8; ID_LEN]>) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(12 + ids.len() * ID_LEN);
    bytes.extend_from_slice(JOURNAL_MAGIC);
    bytes.extend_from_slice(&JOURNAL_VERSION.to_le_bytes());
    bytes.extend_from_slice(&(ids.len() as u32).to_le_bytes());
    for id in ids { bytes.extend_from_slice(id); }
    bytes
}

fn decode_command_history(bytes: &[u8]) -> Result<BTreeSet<[u8; ID_LEN]>, CswResult> {
    if bytes.len() < 12 || &bytes[..4] != JOURNAL_MAGIC { return Err(CswResult::CorruptData); }
    let version = u32::from_le_bytes(bytes[4..8].try_into().map_err(|_| CswResult::CorruptData)?);
    if version != JOURNAL_VERSION { return Err(CswResult::UnsupportedVersion); }
    let count = u32::from_le_bytes(bytes[8..12].try_into().map_err(|_| CswResult::CorruptData)?) as usize;
    if count > MAX_ACCEPTED_COMMAND_IDS || bytes.len() != 12 + count * ID_LEN { return Err(CswResult::CorruptData); }
    let mut ids = BTreeSet::new();
    for chunk in bytes[12..].chunks_exact(ID_LEN) {
        let id: [u8; ID_LEN] = chunk.try_into().map_err(|_| CswResult::CorruptData)?;
        if !ids.insert(id) { return Err(CswResult::CorruptData); }
    }
    Ok(ids)
}

fn refresh_save_integrity(runtime: &mut Runtime) {
    runtime.journal_checkpoint = encode_command_history(&runtime.accepted_command_ids);
    runtime.canonical_hash = canonical_hash(&runtime.campaign_id, &runtime.rules_manifest_hash, runtime.tick, runtime.revision, &runtime.snapshot, &runtime.journal_checkpoint);
    runtime.checksum = checksum_hash(&runtime.canonical_hash);
}

fn runtime_from_save(bytes: *const u8, len: usize) -> Result<Runtime, CswResult> {
    let slice = unsafe { std::slice::from_raw_parts(bytes, len) };
    let envelope = root_as_envelope(slice).map_err(|_| CswResult::CorruptData)?;
    let save = envelope.payload_as_save_envelope().ok_or(CswResult::SchemaMismatch)?;
    let campaign_id = save.campaign_id().ok_or(CswResult::CorruptData)?.bytes().to_vec();
    let rules_hash = save.rules_manifest_hash().ok_or(CswResult::CorruptData)?.bytes().to_vec();
    let canonical = save.canonical_hash().ok_or(CswResult::CorruptData)?.bytes().to_vec();
    let checksum = save.checksum().ok_or(CswResult::CorruptData)?.bytes().to_vec();
    let journal_checkpoint = save.journal_checkpoint().ok_or(CswResult::CorruptData)?.bytes().to_vec();
    let accepted_command_ids = decode_command_history(&journal_checkpoint)?;
    Ok(Runtime {
        initialized: true,
        tick: save.tick(),
        revision: save.revision(),
        last_sequence: 0,
        last_error: Vec::new(),
        campaign_id: campaign_id.try_into().map_err(|_| CswResult::CorruptData)?,
        rules_manifest_hash: rules_hash.try_into().map_err(|_| CswResult::CorruptData)?,
        snapshot: save.snapshot().ok_or(CswResult::CorruptData)?.bytes().to_vec(),
        journal_checkpoint,
        canonical_hash: canonical.try_into().map_err(|_| CswResult::CorruptData)?,
        checksum: checksum.try_into().map_err(|_| CswResult::CorruptData)?,
        accepted_command_ids,
        last_decisions: Vec::new(),
        projection_base_revision: save.revision(),
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

fn save_bytes(runtime: &Runtime) -> Result<Vec<u8>, CswResult> {
    if !runtime.initialized { return Err(CswResult::InvalidState); }
    if canonical_hash(&runtime.campaign_id, &runtime.rules_manifest_hash, runtime.tick, runtime.revision, &runtime.snapshot, &runtime.journal_checkpoint) != runtime.canonical_hash
        || checksum_hash(&runtime.canonical_hash) != runtime.checksum
    { return Err(CswResult::CorruptData); }
    let mut builder = flatbuffers::FlatBufferBuilder::new();
    let campaign = builder.create_vector(&runtime.campaign_id);
    let rules = builder.create_vector(&runtime.rules_manifest_hash);
    let snapshot = builder.create_vector(&runtime.snapshot);
    let checkpoint = builder.create_vector(&runtime.journal_checkpoint);
    let canonical = builder.create_vector(&runtime.canonical_hash);
    let checksum = builder.create_vector(&runtime.checksum);
    let save = SaveEnvelope::create(&mut builder, &SaveEnvelopeArgs {
        abi_version: ABI_VERSION, schema_version: SCHEMA_VERSION, save_version: SAVE_VERSION,
        rng_version: RNG_VERSION, campaign_id: Some(campaign), rules_manifest_hash: Some(rules),
        tick: runtime.tick, revision: runtime.revision, snapshot: Some(snapshot),
        journal_checkpoint: Some(checkpoint), canonical_hash: Some(canonical), checksum: Some(checksum),
    });
    let payload = save.as_union_value();
    let envelope = Envelope::create(&mut builder, &EnvelopeArgs { payload_type: RootPayload::SaveEnvelope, payload: Some(payload) });
    builder.finish(envelope, Some("CSWP"));
    Ok(builder.finished_data().to_vec())
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
        let runtime = Box::new(Runtime { initialized: false, tick: 0, revision: 0, last_sequence: 0, last_error: Vec::new(), campaign_id: [0; 16], rules_manifest_hash: [0; 32], snapshot: Vec::new(), journal_checkpoint: Vec::new(), canonical_hash: [0; 32], checksum: [0; 32], accepted_command_ids: BTreeSet::new(), last_decisions: Vec::new(), projection_base_revision: 0 });
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
        let value = match runtime_ref(runtime.cast_const()) { Ok(value) => value, Err(error) => return error };
        let bytes = std::slice::from_raw_parts(batch, batch_len);
        let base_revision = value.revision;
        let decoded = command::decode_command_batch(bytes, value);
        let rejected_code = decoded.as_ref().err().map(|_| command::rejection_code(bytes, value));
        let runtime = &mut *(runtime.cast::<Runtime>());
        match decoded {
            Ok(candidate) => {
                runtime.accepted_command_ids.extend(&candidate);
                runtime.revision = runtime.revision.saturating_add(1);
                runtime.last_decisions = candidate.into_iter().map(|command_id| DecisionRecord {
                    command_id, code: DecisionCode::Accepted, validated_revision: runtime.revision,
                }).collect();
                runtime.projection_base_revision = base_revision;
                refresh_save_integrity(runtime);
                CswResult::Ok
            }
            Err(error) => {
                let code = rejected_code.unwrap_or(DecisionCode::RejectedByPolicy);
                runtime.last_decisions = command::decision_ids(bytes).into_iter().map(|command_id| DecisionRecord {
                    command_id, code, validated_revision: runtime.revision,
                }).collect();
                runtime.projection_base_revision = runtime.revision;
                error
            }
        }
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
            let base_revision = runtime.revision;
            runtime.tick = runtime.tick.saturating_add(u64::from(max_ticks));
            runtime.revision = runtime.revision.saturating_add(1);
            runtime.last_decisions.clear();
            runtime.projection_base_revision = base_revision;
            if runtime.initialized { refresh_save_integrity(runtime); }
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
    guarded(|| unsafe { runtime_ref(runtime.cast_const()).map_or_else(|error| error, |value| match projection_bytes(value) { Ok(bytes) => copy_bytes(out, out_len, required_len, &bytes), Err(error) => error }) })
}

#[unsafe(no_mangle)]
pub extern "C" fn csw_save_into(
    runtime: *mut CswRuntime,
    out: *mut u8,
    out_len: usize,
    required_len: *mut usize,
) -> CswResult {
    guarded(|| unsafe { runtime_ref(runtime.cast_const()).map_or_else(|error| error, |value| match save_bytes(value) { Ok(bytes) => copy_bytes(out, out_len, required_len, &bytes), Err(error) => error }) })
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
#[path = "tests.rs"]
mod tests;
