use super::*;

pub(super) fn decode_command_batch(
    bytes: &[u8],
    runtime: &Runtime,
) -> Result<Vec<[u8; ID_LEN]>, CswResult> {
    if !runtime.initialized {
        return Err(CswResult::InvalidState);
    }
    let envelope = root_as_envelope(bytes).map_err(|_| CswResult::CorruptData)?;
    let batch = envelope
        .payload_as_command_batch()
        .ok_or(CswResult::SchemaMismatch)?;
    if batch.schema_version() != SCHEMA_VERSION {
        return Err(CswResult::UnsupportedVersion);
    }
    let commands = batch.commands().ok_or(CswResult::InvalidArgument)?;
    if commands.is_empty() || commands.len() > MAX_COMMANDS_PER_BATCH {
        return Err(CswResult::BudgetExceeded);
    }
    let mut candidate_ids = BTreeSet::new();
    for command in commands {
        let command_id = command.command_id().ok_or(CswResult::InvalidArgument)?;
        let campaign_id = command.campaign_id().ok_or(CswResult::InvalidArgument)?;
        let issuer_id = command.issuer_id().ok_or(CswResult::InvalidArgument)?;
        let payload = command.payload().ok_or(CswResult::InvalidArgument)?;
        if command_id.len() != ID_LEN
            || campaign_id.len() != ID_LEN
            || issuer_id.len() != ID_LEN
            || campaign_id.bytes() != runtime.campaign_id
            || payload.is_empty()
            || command.kind() == CommandKind::None
            || command.submitted_tick() > command.scheduled_tick()
        {
            return Err(CswResult::InvalidArgument);
        }
        if command.expected_revision() != runtime.revision {
            return Err(CswResult::RevisionConflict);
        }
        let id: [u8; ID_LEN] = command_id
            .bytes()
            .try_into()
            .map_err(|_| CswResult::InvalidArgument)?;
        if runtime.accepted_command_ids.contains(&id) || !candidate_ids.insert(id) {
            return Err(CswResult::InvalidArgument);
        }
    }
    Ok(candidate_ids.into_iter().collect())
}

pub(super) fn decision_ids(bytes: &[u8]) -> Vec<[u8; ID_LEN]> {
    let Ok(envelope) = root_as_envelope(bytes) else {
        return Vec::new();
    };
    let Some(batch) = envelope.payload_as_command_batch() else {
        return Vec::new();
    };
    let Some(commands) = batch.commands() else {
        return Vec::new();
    };
    let mut ids = BTreeSet::new();
    for command in commands {
        if let Some(id) = command.command_id().filter(|id| id.len() == ID_LEN)
            && let Ok(id) = <[u8; ID_LEN]>::try_from(id.bytes())
        {
            ids.insert(id);
        }
    }
    ids.into_iter().collect()
}

pub(super) fn rejection_code(bytes: &[u8], runtime: &Runtime) -> DecisionCode {
    let Ok(envelope) = root_as_envelope(bytes) else {
        return DecisionCode::RejectedByPolicy;
    };
    let Some(batch) = envelope.payload_as_command_batch() else {
        return DecisionCode::RejectedByPolicy;
    };
    let Some(commands) = batch.commands() else {
        return DecisionCode::RejectedByPolicy;
    };
    for command in commands {
        if command.expected_revision() != runtime.revision {
            return DecisionCode::RevisionConflict;
        }
        if let Some(vector) = command.command_id().filter(|id| id.len() == ID_LEN) {
            let Ok(id) = <[u8; ID_LEN]>::try_from(vector.bytes()) else {
                continue;
            };
            if runtime.accepted_command_ids.contains(&id) {
                return DecisionCode::Duplicate;
            }
        }
    }
    DecisionCode::RejectedByPolicy
}
