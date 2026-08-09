    use flatbuffers::FlatBufferBuilder;
    use crate::warfare_generated::civic_survival::warfare::contracts::{
        CommandBatch, CommandBatchArgs, CommandEnvelope, CommandEnvelopeArgs, CommandKind,
        Envelope, EnvelopeArgs, SaveEnvelope, SaveEnvelopeArgs,
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

    fn command_batch(command_id: &[u8], expected_revision: u64) -> Vec<u8> {
        let mut builder = FlatBufferBuilder::new();
        let command_id = builder.create_vector(command_id);
        let campaign_id = builder.create_vector(&[0x11u8; 16]);
        let issuer_id = builder.create_vector(&[0x12u8; 16]);
        let payload = builder.create_vector(&[0x01u8]);
        let command = CommandEnvelope::create(&mut builder, &CommandEnvelopeArgs {
            command_id: Some(command_id), campaign_id: Some(campaign_id), issuer_id: Some(issuer_id),
            submitted_tick: 1, scheduled_tick: 1, priority: 0, expected_revision,
            kind: CommandKind::Mobilize, payload: Some(payload),
        });
        let commands = builder.create_vector(&[command]);
        let batch = CommandBatch::create(&mut builder, &CommandBatchArgs {
            schema_version: SCHEMA_VERSION, commands: Some(commands),
        });
        let envelope = Envelope::create(&mut builder, &EnvelopeArgs {
            payload_type: RootPayload::CommandBatch, payload: Some(batch.as_union_value()),
        });
        builder.finish(envelope, Some("CSWP"));
        builder.finished_data().to_vec()
    }

    fn valid_save_envelope() -> Vec<u8> {
        let mut builder = FlatBufferBuilder::new();
        let campaign_id = builder.create_vector(&[0x11u8; 16]);
        let rules_hash = builder.create_vector(&[0x22u8; 32]);
        let snapshot = builder.create_vector(&[0x33u8, 0x44]);
        let checkpoint_bytes = encode_command_history(&BTreeSet::new());
        let checkpoint = builder.create_vector(&checkpoint_bytes);
        let canonical = canonical_hash(&[0x11u8; 16], &[0x22u8; 32], 7, 9, &[0x33, 0x44], &checkpoint_bytes);
        let checksum_value = checksum_hash(&canonical);
        let canonical_hash = builder.create_vector(&canonical);
        let checksum = builder.create_vector(&checksum_value);
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
        assert_eq!(csw_save_into(handle, ptr::null_mut(), 0, &mut required), CswResult::InvalidState);
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
        assert_eq!(csw_submit_commands(handle, command_batch.as_ptr(), command_batch.len()), CswResult::InvalidState);

        let save = valid_save_envelope();
        let mut loaded = ptr::null_mut();
        assert_eq!(csw_load(save.as_ptr(), save.len(), &mut loaded), CswResult::Ok);
        assert!(!loaded.is_null());
        let mut status = [0; STATUS_LEN];
        let mut required = 0;
        assert_eq!(csw_status_into(loaded, status.as_mut_ptr(), status.len(), &mut required), CswResult::Ok);
        assert_eq!(u64::from_le_bytes(status[16..24].try_into().unwrap()), 7);
        assert_eq!(u64::from_le_bytes(status[24..32].try_into().unwrap()), 9);
        let mut save_required = 0;
        assert_eq!(csw_save_into(loaded, ptr::null_mut(), 0, &mut save_required), CswResult::BufferTooSmall);
        let mut saved_bytes = vec![0u8; save_required];
        assert_eq!(csw_save_into(loaded, saved_bytes.as_mut_ptr(), saved_bytes.len(), &mut save_required), CswResult::Ok);
        let mut round_tripped = ptr::null_mut();
        assert_eq!(csw_load(saved_bytes.as_ptr(), saved_bytes.len(), &mut round_tripped), CswResult::Ok);
        let mut round_status = [0; STATUS_LEN];
        assert_eq!(csw_status_into(round_tripped, round_status.as_mut_ptr(), round_status.len(), &mut required), CswResult::Ok);
        assert_eq!(round_status, status);
        let mut tampered = saved_bytes.clone();
        let last = tampered.len() - 1;
        tampered[last] ^= 1;
        let mut rejected = ptr::null_mut();
        assert_eq!(csw_load(tampered.as_ptr(), tampered.len(), &mut rejected), CswResult::CorruptData);
        assert!(rejected.is_null());
        csw_destroy(round_tripped);
        csw_destroy(loaded);
        csw_destroy(handle);
    }

    #[test]
    fn command_batches_reject_invalid_ids_without_mutating_loaded_runtime() {
        let save = valid_save_envelope();
        let mut handle = ptr::null_mut();
        assert_eq!(csw_load(save.as_ptr(), save.len(), &mut handle), CswResult::Ok);
        let mut before = [0; STATUS_LEN];
        let mut required = 0;
        assert_eq!(csw_status_into(handle, before.as_mut_ptr(), before.len(), &mut required), CswResult::Ok);
        let invalid = command_batch(&[0xAB], 9);
        assert_eq!(csw_submit_commands(handle, invalid.as_ptr(), invalid.len()), CswResult::InvalidArgument);
        let mut after = [0; STATUS_LEN];
        assert_eq!(csw_status_into(handle, after.as_mut_ptr(), after.len(), &mut required), CswResult::Ok);
        assert_eq!(after, before);
        csw_destroy(handle);
    }

    #[test]
    fn command_batch_commits_once_and_rejects_a_previously_accepted_id() {
        let save = valid_save_envelope();
        let mut handle = ptr::null_mut();
        assert_eq!(csw_load(save.as_ptr(), save.len(), &mut handle), CswResult::Ok);
        let accepted = command_batch(&[0xAB; 16], 9);
        assert_eq!(csw_submit_commands(handle, accepted.as_ptr(), accepted.len()), CswResult::Ok);
        let mut after_accept = [0; STATUS_LEN];
        let mut required = 0;
        assert_eq!(csw_status_into(handle, after_accept.as_mut_ptr(), after_accept.len(), &mut required), CswResult::Ok);
        assert_eq!(u64::from_le_bytes(after_accept[24..32].try_into().unwrap()), 10);
        let duplicate = command_batch(&[0xAB; 16], 10);
        assert_eq!(csw_submit_commands(handle, duplicate.as_ptr(), duplicate.len()), CswResult::InvalidArgument);
        let mut after_duplicate = [0; STATUS_LEN];
        assert_eq!(csw_status_into(handle, after_duplicate.as_mut_ptr(), after_duplicate.len(), &mut required), CswResult::Ok);
        assert_eq!(after_duplicate, after_accept);
        csw_destroy(handle);
    }

    #[test]
    fn command_history_survives_save_and_load() {
        let save = valid_save_envelope();
        let mut handle = ptr::null_mut();
        assert_eq!(csw_load(save.as_ptr(), save.len(), &mut handle), CswResult::Ok);
        let accepted = command_batch(&[0xCD; 16], 9);
        assert_eq!(csw_submit_commands(handle, accepted.as_ptr(), accepted.len()), CswResult::Ok);
        let mut required = 0;
        assert_eq!(csw_save_into(handle, ptr::null_mut(), 0, &mut required), CswResult::BufferTooSmall);
        let mut persisted = vec![0; required];
        assert_eq!(csw_save_into(handle, persisted.as_mut_ptr(), persisted.len(), &mut required), CswResult::Ok);
        let mut restored = ptr::null_mut();
        assert_eq!(csw_load(persisted.as_ptr(), persisted.len(), &mut restored), CswResult::Ok);
        let replay = command_batch(&[0xCD; 16], 10);
        assert_eq!(csw_submit_commands(restored, replay.as_ptr(), replay.len()), CswResult::InvalidArgument);
        csw_destroy(restored);
        csw_destroy(handle);
    }
use crate::*;
use std::collections::BTreeSet;
use std::ptr;
