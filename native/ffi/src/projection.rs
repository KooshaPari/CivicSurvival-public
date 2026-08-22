use super::*;
use crate::warfare_generated::civic_survival::warfare::contracts::{
    CommandDecision, CommandDecisionArgs, ProjectionDelta, ProjectionDeltaArgs,
};

#[derive(Clone, Copy)]
pub(super) struct DecisionRecord {
    pub(super) command_id: [u8; ID_LEN],
    pub(super) code: DecisionCode,
    pub(super) validated_revision: u64,
}

pub(super) fn projection_bytes(runtime: &Runtime) -> Result<Vec<u8>, CswResult> {
    if !runtime.initialized {
        return Err(CswResult::InvalidState);
    }
    let mut builder = flatbuffers::FlatBufferBuilder::new();
    let mut decisions = Vec::with_capacity(runtime.last_decisions.len());
    for record in &runtime.last_decisions {
        let command_id = builder.create_vector(&record.command_id);
        let reason =
            builder.create_string(record.code.variant_name().unwrap_or("RejectedByPolicy"));
        decisions.push(CommandDecision::create(
            &mut builder,
            &CommandDecisionArgs {
                command_id: Some(command_id),
                code: record.code,
                reason_key: Some(reason),
                validated_revision: record.validated_revision,
                details: None,
            },
        ));
    }
    let decisions = builder.create_vector(&decisions);
    let campaign_id = builder.create_vector(&runtime.campaign_id);
    let observer_id = builder.create_vector(&[0u8; ID_LEN]);
    let state_hash = builder.create_vector(&runtime.canonical_hash);
    let delta = ProjectionDelta::create(
        &mut builder,
        &ProjectionDeltaArgs {
            campaign_id: Some(campaign_id),
            observer_id: Some(observer_id),
            base_revision: runtime.projection_base_revision,
            new_revision: runtime.revision,
            tick: runtime.tick,
            state_hash: Some(state_hash),
            decisions: Some(decisions),
            outcomes: None,
            views: None,
            removals: None,
            alerts: None,
            explanations: None,
        },
    );
    let envelope = Envelope::create(
        &mut builder,
        &EnvelopeArgs {
            payload_type: RootPayload::ProjectionDelta,
            payload: Some(delta.as_union_value()),
        },
    );
    builder.finish(envelope, Some("CSWP"));
    Ok(builder.finished_data().to_vec())
}
