# Civic Warfare Canonical Data Model

All IDs are stable 128-bit values or versioned compact IDs allocated deterministically. Runtime graph/ECS indices are never serialized identity. Authoritative numeric quantities use integer or fixed-point domain types with explicit units.

## Identity, Configuration, and Time

| Aggregate     | Required fields/invariants                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Campaign      | id, seed, preset, rules manifest hash, schema/ABI/RNG versions, start/current tick; immutable identity |
| TickState     | tick, revision, sequence high-water marks, per-context hashes; monotonic                               |
| RulesManifest | content IDs/versions/hashes, enabled contexts, scale, difficulty rules; frozen after campaign start    |
| Setting       | key, typed value, mutability class, dependencies; validated before application                         |

## Geography and Infrastructure

| Aggregate     | Required fields/invariants                                                              |
| ------------- | --------------------------------------------------------------------------------------- |
| Theater       | id, regions, active detail policy, climate, strategic bounds                            |
| Settlement    | id, owner/controller, population, districts, government, stockpiles, damage, legitimacy |
| RegionNode    | id, kind, position, terrain, elevation, cover, capacity, owner/controller, condition    |
| RouteEdge     | id, mode, endpoints, distance, capacity, condition, access, interdiction, congestion    |
| AirRegion     | id, weather, detection, control, bases, active missions                                 |
| SeaZone       | id, sea state, straits, ports, detection, control, mines, active missions               |
| StrategicSite | id, type, location, owner, staff, utilities, condition, capacity, target value          |

## Factions and Statecraft

| Aggregate     | Required fields/invariants                                                                     |
| ------------- | ---------------------------------------------------------------------------------------------- |
| Faction       | id, government, ideology, leadership, doctrine, treasury, legitimacy, goals, red lines, memory |
| InternalActor | id, faction, type, constituency, resources, influence, loyalty, grievances, agenda             |
| Relation      | faction pair, recognition, trust, fear, grievances, claims, dependencies, last revision        |
| Agreement     | id, parties, clauses, start/end, compliance, guarantees, breach rules, visibility              |
| Sovereignty   | territory, legal owner, controller, occupation regime, autonomy, claims, resistance            |
| Negotiation   | id, participants, offers, demands, deadline, leverage, constraints, status, outcome            |

## Intelligence and Covert Action

| Aggregate         | Required fields/invariants                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| KnowledgeEstimate | observer, subject, claim type, value/distribution, confidence, source set, observed tick, decay |
| Source            | id, owner, type, access, reliability, security, compromise, cost                                |
| AgentNetwork      | id, owner, target, cells, handlers, access, cover, loyalty, exposure, communications            |
| CovertOperation   | id, sponsor, target, objective, assets, phases, risk, attribution, status, blowback             |
| Investigation     | id, event, investigators, evidence, hypotheses, confidence, public attribution                  |

## Economy, Construction, and Logistics

| Aggregate           | Required fields/invariants                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| ResourceDefinition  | id, unit, category, storage/transport rules, substitutes, civilian/military uses                        |
| Firm                | id, owner, sites, workforce, capital, capacity, inputs, outputs, quality, finances, corruption exposure |
| ProcurementContract | id, buyer, supplier, items, price, milestones, quality, penalties, status, leakage                      |
| ConstructionProject | id, site, design, land/material/labor/utility needs, phases, maintenance, externalities                 |
| Stockpile           | holder/site, resource, on-hand, reserved, damaged, target/min/max; nonnegative conservation             |
| Shipment            | id, source, destination, cargo, route, transport, escort, priority, losses, ETA, status                 |
| LogisticsRequest    | demander, resource, quantity, priority, deadline, substitutions, fulfillment trace                      |
| FlowTrace           | request, considered paths, constrained nodes/edges, allocations, loss/delay, remedy list                |

## Population and Forces

| Aggregate        | Required fields/invariants                                                                                 |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| PopulationCohort | settlement, age/skill/occupation/household/health/loyalty dimensions, count; conserved                     |
| PersonnelPool    | faction, status, skills, training, availability, casualties, obligations                                   |
| EquipmentPool    | faction/site, equipment type, ready/damaged/repair/reserved quantities                                     |
| Formation        | id, faction, HQ, echelon, template, personnel, equipment, readiness, morale, cohesion, fatigue, experience |
| Headquarters     | id, commander, staff, command capacity, subordinate IDs, communications, location                          |
| ForceAssignment  | formation, operation, role, start/end, command relationship, priority                                      |
| CasualtyRecord   | event, cohort/personnel source, killed/wounded/missing/prisoner/deserted, recovery/disposition             |

## Operations and Combat

| Aggregate      | Required fields/invariants                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| Operation      | id, owner, type, objective graph, phases, forces, boundaries, routes, logistics, authorization, risk, status |
| OperationPhase | id, entry/exit conditions, tasks, timing, reserves, contingencies, abort criteria                            |
| Mission        | id, domain, region/zone, assigned assets, posture, rules, schedule, resource budget, status                  |
| ControlState   | node/edge, controller, contesting forces, fortification, last outcome                                        |
| Engagement     | id, domain, participants, location, start/end, conditions, decisions, losses, control/damage outcomes        |
| DefenseWork    | id, type, geometry/direction, staff, supply, condition, concealment, field of fire, bypass routes            |
| DamageState    | target, structural/system damage, fires, hazards, repair tasks, civilian impact                              |

## Civil Resilience

| Aggregate         | Required fields/invariants                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| CivilState        | settlement/region, legitimacy, trust, fear, grievance, scarcity, cohesion, repression, resilience |
| CivilEvent        | id, type, actors, demands, participants, location, intensity, security response, outcome          |
| DisplacementFlow  | origin, destination, people/cohorts, cause, route, needs, status                                  |
| PolicyAction      | id, authority, type, target, budget, duration, legal basis, expected/actual effects               |
| CorruptionNetwork | id, members, sectors, flows, protection, exposure, enforcement/reform state                       |

## Commands, Outcomes, Projections, and Saves

| Record             | Required fields/invariants                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| CommandEnvelope    | command ID, campaign, issuer, submitted/scheduled tick, priority, expected revision, payload; idempotent            |
| CommandDecision    | command ID, accepted/rejected, stable reason, validated revision, resource reservations                             |
| OutcomeEnvelope    | command ID optional, tick, global sequence, context, kind, payload; immutable ordered fact                          |
| ProjectionSnapshot | campaign, revision, tick, knowledge owner, schema version, typed views, state hash                                  |
| ProjectionDelta    | base/new revision, ordered replacements/removals, alerts/explanations, required buffer length; framed by `Envelope` |
| SaveEnvelope       | versions, manifest hash, tick/revision, snapshot bytes, journal checkpoint, checksum/hash                           |
| ExplanationTrace   | subject/decision, perceived inputs, alternatives/scores, constraints, decision, uncertainty, result                 |

## Conservation and Ownership Invariants

- Population moves between cohorts/personnel/casualty/displacement states; it is never created by mobilization or LOD.
- Equipment/resources move through production, stockpile, shipment, assignment, use, damage, repair, or loss ledgers.
- Every territory/site has one legal owner and at most one controller at a revision; contest is separate state.
- Every authoritative aggregate has one context writer per tick stage.
- Every accepted command produces a terminal decision and zero or more ordered outcomes exactly once.
- Aggregate/detail promotion round-trips canonical quantities and pending commands exactly.
