# Specification: Civic Warfare and Resilient City Program

**Slug**: civic-warfare-program | **Date**: 2026-07-22 | **State**: specified
**Baseline**: CivicSurvival v0.3.24, commit `0b218074`
**Target Branch**: `main` on `KooshaPari/CivicSurvival-public`

## Mission

Turn CivicSurvival into a grand-theater city-survival simulation in which the city economy, population, infrastructure, diplomacy, intelligence, and civil legitimacy exist to sustain credible defense and war. The player is supreme commander and mayor through two co-primary spaces: the real Cities: Skylines II home city and a persistent War Room theater containing foreign settlements, factions, fronts, air regions, sea zones, and operations.

The system supports ground, air, maritime, amphibious, airborne, covert, civil-defense, and occupation play. It uses operational command rather than per-unit RTS control, rule-symmetric AI factions, selective-detail simulation, and fully configurable sandbox, finite campaign, and endless-survival presets.

## Locked Product Decisions

- Rust is the authoritative deterministic theater runtime behind a narrow C ABI; C# owns Unity/ECS integration, saves, rendering, and game adapters; TypeScript/React owns the UI.
- Python and Julia are offline scenario, calibration, analytics, and balance tools. Zig may own reproducible cross-link/ABI tooling after a benchmark. Mojo is experimental only. Nim, Pony, and Vale are research-only unless a future ADR proves unique measurable benefit.
- The simulation is a modular monolith using functional-core/imperative-shell, hexagonal ports at ownership boundaries, bounded contexts, CQRS-style immutable projections, snapshots plus a command/outcome journal, and no actor model or second generic ECS in the authoritative Rust core.
- Detailed and aggregate simulation use identical canonical resources and rules. Promotion/demotion preserves population, equipment, stockpiles, damage, experience, morale, and orders exactly.
- All mechanics and autonomy levels are configurable. Settings are classified as live, next-tick, or new-campaign-only and validated for dependency conflicts.
- The default Grand Theater preset targets 12 factions, 60 settlements, and 300 formations.
- No production warfare implementation begins until WP01 proves a fresh-clone public C# audit build and baseline test suite.
- Forward-only save schema: no compatibility shims for pre-warfare development saves.

## User Outcomes

1. City planning has legible military consequences: land use, utilities, workers, firms, transport, imports, debt, corruption, and public trust determine readiness.
2. Defense is layered and recoverable: intelligence, diplomacy, deterrence, air/missile defense, field forces, walls, shelters, logistics, reserves, and fallback positions all matter.
3. Invasions are understandable operations with staging, access, lift, supply, superiority, preparation, authorization, and visible risk rather than surprise dice rolls.
4. Foreign factions build, trade, mobilize, negotiate, spy, protest, fracture, fight, occupy, and recover under the same rules.
5. Automation is trustworthy: the player can delegate by domain, constrain doctrine and risk, inspect explanations, and retake control without hidden AI cheats.

## Functional Requirements

### WP01 - Public audit build and baseline quality gate

- **FR-001**: Provide a fresh-clone public audit solution that compiles all game-independent C# assemblies, contracts, analyzers, generators, and tools without proprietary game binaries.
- **FR-002**: Provide a separate installed-game adapter build and native launch smoke lane that verifies CS2/Unity integration when legal local references exist.
- **FR-003**: Add canonical C# unit, contract, integration, save, and deterministic-system test projects with concern-based filenames and a baseline test inventory.
- **FR-004**: Add CI for C#, UI, schemas, dependency/license/security scans, file-size policy, localization parity, privacy assertions, and artifact reproducibility.
- **FR-005**: Reconcile release metadata, diagnostics consent wording, dependency findings, warning suppressions, and current >500-line hotspots before opening the warfare code gate.
- **FR-101**: Publish WP01's reproducible commands, baseline metrics, test inventory, unresolved exceptions, and signed go/no-go evidence as the mandatory warfare implementation gate.

### WP02 - Architecture, contracts, and native boundary

- **FR-006**: Create a Rust workspace whose inward dependency direction separates model, rules, geography, statecraft, economy, logistics, forces, operations, combat, AI, replay, FFI, and headless runner.
- **FR-007**: Generate a versioned C ABI and C# bindings with opaque handles, caller-owned buffers, explicit error enums, ABI handshake, panic containment, and fail-closed warfare disablement.
- **FR-008**: Define one pinned FlatBuffers schema toolchain that generates Rust, C#, TypeScript, and Python command, outcome, projection, rules, and save envelopes with conformance checks.
- **FR-009**: Generalize the existing durable intent-resolution-signal pattern into idempotent ordered commands, exactly-once outcomes, and ephemeral projection signals.
- **FR-010**: Enforce bounded-context and namespace/crate dependency rules through architecture tests; prohibit Unity, filesystem, wall-clock, networking, and UI dependencies inside the Rust domain kernel.
- **FR-102**: Record and test every public boundary's ownership, lifecycle, versioning, batching, allocation, failure, and compatibility policy before dependent lanes begin.

### WP03 - Deterministic simulation, replay, and persistence

- **FR-011**: Resolve authoritative state on fixed integer ticks using fixed-point domain newtypes, stable IDs, stable iteration, explicit tie-breaking, and named deterministic random streams.
- **FR-012**: Implement single-writer staged ticks: ingest observations, validate commands, plan, resolve economy/logistics, resolve operations/combat, apply consequences, then project.
- **FR-013**: Persist versioned snapshots plus append-only player/AI commands and coarse outcomes, with periodic checkpoints, compaction, PRNG version, and canonical BLAKE3 hashes.
- **FR-014**: Provide headless record/replay, golden replay, cross-build hash comparison, desync localization, and deterministic debug traces.
- **FR-015**: Use deterministic parallelism only for read-only scoring or tiles, stable-sort results, and commit mutation serially.
- **FR-103**: Maintain golden vectors for fixed-point arithmetic, random-stream derivation, canonical serialization, state hashing, journal replay, and snapshot restore.

### WP04 - Geography, theater topology, and selective detail

- **FR-016**: Model theaters, settlements, districts, land nodes, air regions, sea zones, borders, access rights, terrain, weather, routes, and strategic infrastructure with stable identity.
- **FR-017**: Maintain road, rail, river, sea, air, power, communications, and supply graphs with capacity, condition, ownership, interdiction, and repair state.
- **FR-018**: Select detail bubbles from player proximity, observation confidence, active operations, risk, and consequence while aggregating distant entities.
- **FR-019**: Promote and demote cohorts deterministically with exact conservation and round-trip hash tests; no separate fake distant model is permitted.
- **FR-020**: Expose terrain, weather, control, detection, threat, logistics, unrest, and opportunity influence layers to planning and War Room overlays.
- **FR-104**: Prove every LOD promotion/demotion path conserves canonical quantities and produces the same later outcomes as continuously detailed simulation within declared tolerances.

### WP05 - Factions, diplomacy, sovereignty, and peace

- **FR-021**: Model peer factions with government, ideology, leadership, constituencies, goals, red lines, legitimacy, memory, doctrine, treasury, territory, and knowledge.
- **FR-022**: Support recognition, relations, grievances, claims, trade, aid, guarantees, alliances, coalitions, sanctions, ceasefires, peace, access, basing, and intelligence-sharing agreements.
- **FR-023**: Resolve negotiation through explicit offers, demands, deadlines, credibility, leverage, domestic constraints, compliance, breach, and explainable acceptance scores.
- **FR-024**: Support occupation, military administration, annexation, autonomy, protectorates, liberation, reparations, demilitarized zones, prisoner exchange, and negotiated withdrawal.
- **FR-025**: Make diplomatic and territorial changes emit ordinary validated commands/outcomes and feed economy, logistics, intelligence, civil stability, and AI without direct cross-context mutation.
- **FR-105**: Provide scenario tests for alliance formation, treaty breach, sanctions, negotiated peace, occupation, autonomy, liberation, and postwar settlement under imperfect information.

### WP06 - War economy, firms, procurement, and military construction

- **FR-026**: Extend the vanilla resource economy with arms, ammunition, fuel, spare parts, electronics, medical supplies, engineering stores, vehicles, aircraft, ships, and strategic reserves.
- **FR-027**: Model firms, ownership, productive capacity, labor, wages, prices, contracts, bids, delivery schedules, quality, substitution, imports, sanctions, corruption, and civilian conversion costs.
- **FR-028**: Make procurement compete with public services, household consumption, construction, debt service, grid capacity, transport, and political approval.
- **FR-029**: Add placeable military districts, bases, barracks, arsenals, depots, airfields, ports, shipyards, repair yards, training grounds, hospitals, shelters, command posts, and coastal works.
- **FR-030**: Give military construction land, labor, material, utility, pollution, noise, maintenance, staffing, target-value, resilience, and public-approval consequences.
- **FR-106**: Balance and verify guns-versus-butter tradeoffs so neither unlimited militarization nor ignoring defense is a dominant strategy across campaign presets.

### WP07 - Unified logistics and sustainment

- **FR-031**: Use one physical chain from production and imports through warehouses, routes, ports, railheads, depots, and distribution to formations and civilian consumers.
- **FR-032**: Track capacity, throughput, priority, distance, handling, transport assets, fuel, spoilage, loss, delay, congestion, damage, repair, and stock policy.
- **FR-033**: Make formations consume food, ammunition, fuel, spares, medical support, engineering stores, and replacements according to posture and combat intensity.
- **FR-034**: Support convoy, escort, reroute, pre-position, emergency airlift/sealift, requisition, interdiction, sabotage, blockade, and depot-dispersal operations.
- **FR-035**: Explain every shortage through a causal trace from demand to constrained edges/nodes, expected recovery, and available player remedies.
- **FR-107**: Validate logistics conservation, priority fairness, rerouting, interdiction, blockade, repair, and recovery with graph properties and reference scenarios.

### WP08 - Population, mobilization, forces, and readiness

- **FR-036**: Recruit militia, reserves, professionals, specialists, volunteers, conscripts, contractors, and mercenaries from population cohorts with household and labor-market effects.
- **FR-037**: Model formations, headquarters, units, equipment pools, personnel, training, cohesion, morale, fatigue, experience, doctrine, command capacity, and readiness.
- **FR-038**: Support tables of organization/equipment, reinforcement priorities, rotation, leave, retraining, refit, demobilization, disbandment, and veteran reintegration.
- **FR-039**: Couple casualties, missing, wounded, prisoners, disability, desertion, and veteran outcomes to demographics, families, productivity, legitimacy, and unrest.
- **FR-040**: Make mobilization staged, politically authorized, financially funded, equipped, trained, transported, housed, and reversible rather than an instant manpower conversion.
- **FR-108**: Prove mobilization, casualties, demobilization, and veteran reintegration conserve population cohorts and correctly alter firms, households, budgets, and legitimacy.

### WP09 - Ground warfare

- **FR-041**: Resolve operational ground movement and combat using terrain, weather, frontage, posture, entrenchment, reconnaissance, initiative, command, supply, fatigue, morale, and combined arms.
- **FR-042**: Support infantry, armor, mechanized, motorized, artillery, engineers, reconnaissance, logistics, special operations, military police, and organic air-defense capabilities.
- **FR-043**: Support advance, defend, delay, screen, probe, assault, breakthrough, exploit, encircle, relieve, counterattack, withdraw, evacuate, surrender, and regroup orders.
- **FR-044**: Model lines of control, contested nodes, reserves, flanks, breakthroughs, pockets, encirclement, river crossings, urban fighting, siege, capture, and occupation transitions.
- **FR-045**: Resolve civilian presence, displacement, infrastructure damage, unexploded ordnance, surrender protection, proportionality, war crimes risk, and post-battle recovery as explicit consequences.
- **FR-109**: Validate ground outcomes against invariant, symmetry, monotonicity, combined-arms, encirclement, withdrawal, urban, and civilian-harm scenario suites.

### WP10 - Air and missile warfare

- **FR-046**: Model air wings, aircraft pools, crews, training, readiness, maintenance, munitions, fuel, range, basing, runway condition, dispersal, and sortie generation.
- **FR-047**: Support air-superiority, interception, escort, close-support, interdiction, reconnaissance, transport, airborne, strategic-strike, electronic-warfare, and suppression missions by region.
- **FR-048**: Resolve detection and engagement through radar, observers, intelligence, weather, altitude, signature, jamming, command links, rules of engagement, and layered defenses.
- **FR-049**: Integrate existing drone, ballistic, Bofors, Gepard, Hawk, and Patriot systems into a generalized air/missile threat and defense model without duplicate ownership.
- **FR-050**: Support airfield attack/repair, runway denial, hardened shelters, decoys, relocation, combat air patrols, ammunition conservation, and civilian airspace constraints.
- **FR-110**: Validate sortie generation, detection, interception, layered defense, suppression, airfield damage, weather grounding, and ammunition exhaustion through deterministic scenarios.

### WP11 - Maritime and littoral warfare

- **FR-051**: Model fleets, task forces, vessels, crews, readiness, fuel, ammunition, damage, maintenance, sensors, range, sea state, ports, and naval command.
- **FR-052**: Support patrol, escort, raid, convoy, blockade, sea-control, sea-denial, mine, minesweeping, strike, shore-bombardment, amphibious-support, and evacuation missions.
- **FR-053**: Resolve detection, contact, pursuit, disengagement, engagement, submarine/littoral risk, air cover, coastal defense, and rules of engagement by sea zone.
- **FR-054**: Make ports, shipyards, anchorages, canals, straits, coastal batteries, maritime trade, convoy capacity, and repair facilities strategic physical assets.
- **FR-055**: Couple maritime outcomes to imports, exports, aid, fuel, food, military lift, insurance, prices, shortages, diplomacy, and civil stability.
- **FR-111**: Validate convoy survival, escort, blockade, mines, port denial, amphibious support, littoral defense, repair, and trade-price consequences through deterministic scenarios.

### WP12 - Fortifications, bases, and home-city defense

- **FR-056**: Support walls, gates, checkpoints, trenches, bunkers, obstacles, minefields, shelters, hardened depots, command posts, coastal batteries, and fallback positions.
- **FR-057**: Make defenses directional, staffed, supplied, maintained, degradable, repairable, bypassable, observable, and integrated with terrain and fields of fire.
- **FR-058**: Support layered defense plans with security zones, evacuation routes, rally points, reserves, counterattack routes, demolition plans, and continuity sites.
- **FR-059**: Integrate civilian shelters, emergency services, hospitals, utilities, stockpiles, warning systems, evacuation, firefighting, debris clearance, and reconstruction.
- **FR-060**: Make military bases and defenses affect land value, access, traffic, noise, pollution, employment, public trust, sabotage risk, and enemy targeting.
- **FR-112**: Validate layered defense, breach, bypass, degradation, repair, evacuation, continuity, fallback, and civilian recovery using home-city reference layouts.

### WP13 - Operations, invasions, and joint command

- **FR-061**: Represent operations as persistent plans with objectives, phases, assigned forces, command relationships, intelligence, logistics, timing, contingencies, risk, and political authorization.
- **FR-062**: Support defensive, offensive, raid, relief, counterattack, withdrawal, evacuation, amphibious, airborne, humanitarian, and stabilization operations.
- **FR-063**: Require invasions to satisfy staging, lift, access, route, supply, readiness, preparation, deception, sea/air control, weather, and sustainment prerequisites.
- **FR-064**: Provide operational command through objectives, axes, boundaries, priorities, reserves, posture, risk tolerance, rules of engagement, and phase lines rather than unit micromanagement.
- **FR-065**: Expose forecasts, confidence, assumptions, unmet prerequisites, likely branches, abort criteria, and after-action results for every operation.
- **FR-113**: Validate joint operations from planning through termination, including rejected prerequisites, phase transitions, contingencies, aborts, command changes, and after-action accounting.

### WP14 - Intelligence, espionage, sabotage, and terrorism

- **FR-066**: Maintain faction-specific knowledge with sources, confidence, age, contradiction, deception risk, access, classification, and explicit decay.
- **FR-067**: Support reconnaissance, surveillance, signals intelligence, human intelligence, counterintelligence, infiltration, influence, cyber, sabotage, theft, deception, and security operations.
- **FR-068**: Model agents, networks, cells, handlers, access, cover, loyalty, exposure, resources, communications, compromise, capture, defection, and blowback.
- **FR-069**: Model terrorism as actor-driven coercion using target selection, capability, intent, opportunity, security, civilian harm, attribution, political effect, and counterproductive backlash.
- **FR-070**: Prevent perfect information: the UI and AI act on their own knowledge snapshots, while post-event investigations can revise attribution and reveal deception.
- **FR-114**: Validate intelligence uncertainty, confidence decay, deception, compromise, attribution revision, counterintelligence, and blowback without exposing hidden truth to decision makers.

### WP15 - Civil resilience, legitimacy, unrest, and corruption

- **FR-071**: Derive legitimacy and unrest from shortages, inequality, casualties, displacement, occupation, corruption, repression, service quality, ideology, expectations, and information.
- **FR-072**: Support petitions, demonstrations, protests, strikes, mutinies, riots, looting, sabotage, insurgency, coups, defections, reconciliation, and peaceful reform.
- **FR-073**: Model unions, parties, ministries, security services, media, oligarchs, civil society, minorities, veterans, refugees, and regional constituencies as internal actors.
- **FR-074**: Make policing, negotiation, concessions, welfare, transparency, censorship, emergency law, targeted security, and repression carry distinct short- and long-term consequences.
- **FR-075**: Connect corruption and shadow-economy networks to procurement, logistics leakage, intelligence compromise, black markets, patronage, inequality, and reform capacity.
- **FR-115**: Validate peaceful protest, strike, riot, insurgency, coup, reform, negotiation, welfare, targeted security, and repression paths without making repression universally optimal.

### WP16 - Strategic AI, autonomy, and explainability

- **FR-076**: Use hierarchical task planning for faction strategy, utility scoring for operations, deterministic behavior trees/state machines for execution, and influence maps for spatial reasoning.
- **FR-077**: Give AI factions the same resources, rules, command costs, knowledge limits, cooldowns, logistics, politics, and fog of war as the player.
- **FR-078**: Support manual, advisory, semi-autonomous, and autonomous control independently for economy, logistics, force generation, ground, air, sea, intelligence, diplomacy, and civil response.
- **FR-079**: Let players constrain delegated intent through doctrine, priorities, protected assets, reserves, loss tolerance, escalation limits, budget ceilings, and approval gates.
- **FR-080**: Emit compact decision traces showing perceived facts, goals, options, scores, constraints, chosen action, rejected alternatives, uncertainty, and later result.
- **FR-116**: Run AI league, adversarial, exploit, non-cheating, personality-diversity, performance, and explanation tests for every autonomy level and faction doctrine.

### WP17 - War Room, city UI, accessibility, and quality of life

- **FR-081**: Make the real city and War Room co-primary views with synchronized selection, time, alerts, forecasts, commands, and outcomes.
- **FR-082**: Provide map layers for control, terrain, weather, detection, air defense, supply, routes, damage, civil risk, unrest, diplomacy, and operation plans.
- **FR-083**: Provide searchable/filterable rosters, order templates, doctrine presets, comparison views, logistics diagnosis, readiness explanations, alerts, and after-action reports.
- **FR-084**: Support pause-and-plan, queued command review, safe cancellation before execution, command history, keyboard navigation, focus management, screen-reader semantics, reduced motion, and color-safe encodings.
- **FR-085**: Maintain complete en-US, uk-UA, and zh-CN key parity; use neutral systemic English and realistic Ukrainian localization/context without hard-coded propaganda or medical inference.
- **FR-117**: Validate every critical workflow by keyboard and assistive semantics, snapshot all supported locales, and performance-test target-scale roster/map updates.

### WP18 - Campaigns, scenarios, content rules, and configuration

- **FR-086**: Run living sandbox objectives, finite campaigns, and endless escalating survival from one simulation core using validated presets.
- **FR-087**: Define versioned data-only rules/content packs for resources, buildings, units, doctrines, operations, factions, events, objectives, victory, defeat, and escalation.
- **FR-088**: Freeze the content registry at campaign start, reject unknown/conflicting IDs, and classify settings as live, next-tick, or new-campaign-only.
- **FR-089**: Provide a Grand Theater default of approximately 12 factions, 60 settlements, and 300 formations plus scalable smaller presets and custom import/export.
- **FR-090**: Support scenario validation, deterministic seeds, scripted initial conditions, objective graphs, difficulty through rules/resources rather than hidden cheats, and shareable reproducible reports.
- **FR-118**: Provide schema, semantic, dependency, balance, determinism, and content-license validation for every built-in and imported preset/rules pack.

### WP19 - Verification, performance, security, and observability

- **FR-091**: Add unit, property, contract, integration, replay, fuzz, mutation, UI, accessibility, localization, native smoke, scenario, performance, and soak suites tied to requirement evidence.
- **FR-092**: Prove deterministic replay through identical hashes for repeated 10,000-tick runs across debug/release and supported Windows x64 build configurations.
- **FR-093**: Enforce target-scale budgets: normal Rust tick p95 at most 5 ms, planning tick p95 at most 25 ms, C# bridge p95 at most 1 ms, and zero steady-state managed allocation on poll/render paths.
- **FR-094**: Fuzz every ABI/schema/save decoder, reject corrupt or incompatible inputs without undefined behavior, contain Rust panics, and disable warfare without crashing the city simulation.
- **FR-095**: Produce structured performance counters, replay/desync diagnostics, AI decision traces, supply causal traces, privacy-safe errors, SBOM, licenses, and dependency vulnerability reports.
- **FR-119**: Make the complete validation suite emit machine-readable FR-to-test-to-evidence records consumable by AgilePlus governance and release gates.

### WP20 - Documentation, licensing, release, and operational readiness

- **FR-096**: Document architecture, contracts, mod build, native toolchain, scenario authoring, balancing, testing, debugging, privacy, security, accessibility, and player mechanics from the implementation truth.
- **FR-097**: Maintain one canonical version across project, manifest, UI, schemas, ABI, save, rules, release notes, and packaged artifacts.
- **FR-098**: Pin dependencies and toolchains, record SPDX provenance and modifications, and require an ADR plus full compatibility review before importing copyleft code or relicensing the project.
- **FR-099**: Package and smoke-test the Windows x64 native library, schemas, C# host, UI bundle, content packs, notices, licenses, and recovery behavior from a clean release environment.
- **FR-100**: Ship only after every FR has linked evidence, every work package is done, governance validation passes, audit chain verifies, documentation matches behavior, and rollback is a package-level version restore rather than runtime compatibility code.
- **FR-120**: Produce a signed release dossier containing provenance, SBOM, licenses, reproducible hashes, test/performance evidence, privacy review, accessibility review, known issues, and recovery instructions.

## Non-Functional Requirements

- **QR-001 Determinism**: Canonical state must be bit-reproducible for identical versioned inputs.
- **QR-002 Performance**: Meet the requirement 093 performance budgets at the Grand Theater reference scale on the documented reference machine.
- **QR-003 Availability**: Native-runtime failure must not corrupt saves or crash the host city simulation.
- **QR-004 Security**: All untrusted content, schemas, saves, and ABI inputs are bounded, validated, and fuzzed.
- **QR-005 Privacy**: Diagnostics remain explicit opt-in, data-minimized, documented, and independently disableable.
- **QR-006 Accessibility**: All critical commands and state are perceivable and operable without color, pointer, animation, or audio alone.
- **QR-007 Localization**: All supported locales maintain exact key and parameter parity in CI.
- **QR-008 Modularity**: Production modules stay below 500 lines, target 350, with explicit ownership and acyclic dependencies.
- **QR-009 Testability**: The authoritative kernel runs headlessly with no Unity or proprietary game dependency.
- **QR-010 Observability**: Every accepted command can be traced to outcomes and projection revisions without logging personal data.
- **QR-011 Explainability**: AI, supply, diplomacy, combat, and civil results expose bounded causal explanations.
- **QR-012 Scalability**: Distant aggregation prevents work from scaling with every citizen or tactical object.
- **QR-013 Maintainability**: Generated contracts are single-source; handwritten mirrored DTOs are prohibited.
- **QR-014 Portability**: Windows x64 ships first; headless Rust tests must run on macOS, Linux, and Windows CI.
- **QR-015 Licensing**: No source is copied or linked without verified provenance and compatible distribution obligations.
- **QR-016 Reproducibility**: Build inputs, generators, schemas, dependencies, and packaged outputs are pinned and hashable.
- **QR-017 Integrity**: Saves and journals include versions, lengths, checksums, and canonical state hashes.
- **QR-018 Usability**: Every failed prerequisite or rejected order includes a reason and actionable remedy.
- **QR-019 Fairness**: Difficulty may change declared rules/resources but never grant AI hidden information or mutation paths.
- **QR-020 Governance**: Progress is derived from AgilePlus work-package state plus acceptance evidence, not handwritten percentages.

## Acceptance Gate

The program is specification-complete when all 120 FRs map to one of 20 work packages, the dependency graph is acyclic, public contracts and data ownership are explicit, every WP has runnable validation/evidence requirements, and AgilePlus dashboard state can be updated without editing this document. Production implementation remains blocked until WP01 passes.
