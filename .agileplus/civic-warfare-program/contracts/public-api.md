# Public Contract Specification

## ABI Lifecycle

| Function | Behavior |
|---|---|
| `csw_abi_version` | returns packed major/minor ABI version without initialization |
| `csw_create` | validates config/rules buffer and returns opaque runtime handle |
| `csw_load` | validates complete save before replacing handle state |
| `csw_submit_commands` | validates one FlatBuffers batch and queues idempotent commands |
| `csw_step` | advances a bounded number of fixed ticks from one observation batch |
| `csw_poll_into` | writes one projection/outcome batch into caller buffer or reports required size |
| `csw_save_into` | writes canonical snapshot/journal checkpoint into caller buffer |
| `csw_status` | returns non-allocating health/version/tick/revision counters |
| `csw_last_error_into` | copies bounded diagnostic text for the calling thread/handle |
| `csw_destroy` | invalidates and releases handle; null is a no-op |

All calls return `CswResult`. Buffers are `(pointer,length)` byte spans. No Rust/C# strings, collections, structs with language-dependent layout, callbacks, exceptions, or ownership ambiguity cross the ABI. Output functions never partially encode a record. Every call is panic-contained.

## Stable Errors

`Ok`, `BufferTooSmall`, `InvalidArgument`, `InvalidHandle`, `InvalidState`, `AbiMismatch`, `SchemaMismatch`, `RulesMismatch`, `RevisionConflict`, `DuplicateCommand`, `CommandRejected`, `CorruptData`, `UnsupportedVersion`, `BudgetExceeded`, `DeterminismFailure`, `InternalPanic`.

Recoverable command rejection belongs in `CommandDecision`; ABI errors describe transport/runtime failure.

## Command Ordering and Idempotency

The kernel deduplicates `command_id`. Accepted same-tick commands sort by scheduled tick, command priority, issuer ID, submitted tick, then command ID. Expected-revision mismatch rejects without reservation. Cross-context effects become outcomes consumed in the declared later stage or commands for a later tick.

## Schema Evolution

- FlatBuffers field IDs are never reused; removed fields remain reserved.
- New optional fields and enum values require old-reader behavior tests.
- Required semantic changes increment schema major and save major.
- `flatc --conform` compares every revision to the checked-in baseline.
- Generator/runtime/compiler versions are one lockstep toolchain.
- Unknown content IDs fail campaign validation; unknown optional projection fields are ignored by old views.

## C# Host Ports

```csharp
public interface IWarfareRuntime : IDisposable
{
    WarfareStatus Status { get; }
    CommandBatchResult Submit(ReadOnlySpan<byte> commandBatch);
    StepResult Step(ReadOnlySpan<byte> observations, uint maxTicks);
    PollResult Poll(Span<byte> destination);
    SaveResult Save(Span<byte> destination);
}

public interface ICityObservationSource
{
    CityObservationBatch Capture(long cityTick, ulong revision);
}

public interface IWarfareProjectionSink
{
    void Apply(WarfareProjectionBatch batch);
}
```

The composition root owns implementations. Existing domains interact only through typed command/query facades; UI emits commands and never mutates ECS/domain state.

## Domain Application Ports

Rust application ports are narrow capabilities: `SpatialIndex`, `Planner`, `RandomStreams`, `EventSink`, `SnapshotStore`, `ProjectionSink`, `RulesProvider`, and `PerformanceSink`. Domain reducers receive explicit references; no global registry/service locator exists inside the kernel.

## Save Contract

Load is transactional: decode header and bounds, verify checksum/hash, verify ABI/schema/rules/RNG versions, decode to temporary canonical state, validate invariants, then swap. Failure leaves prior state and source bytes untouched. There is no legacy warfare save shim.

## Projection Contract

Projection batches are immutable and knowledge-scoped. A projection declares campaign, observer faction/player, base revision, new revision, tick, state hash, changed views, removals, alerts, command decisions, and explanations. C# rejects gaps and requests a full snapshot; it never guesses missing deltas.
