# Production workflow

This workflow prepares Quran recitation and Indonesian translation narration for a reviewed native editing session. It distills the current production method (D092), including the later complete-word and internal-boundary rules (D133–D134). Source recordings, canonical text, account data and production records are supplied by the operator and are not included here.

The tools in this repository assist individual steps. This document does not claim that every rule is enforced automatically or that a complete production pipeline has been implemented. See [production rules](production-rules.md) for wording, approval and preservation requirements.

## 1. Establish the source and authorized scope

Confirm the chapter and verse range, language, translation edition, recording and narration voice. Preserve canonical Arabic, translation, verse references and source provenance separately from the spoken derivative. Use material whose permissions cover the intended use.

Load the latest approved text, audio, maps and production state. Reuse completed analysis when its source hash still matches. A handoff or changed editing session does not invalidate unchanged source evidence. Record the current native timeline, source identities, positions, fades, effects and clip Volume before proposing edits; preserve a recoverable baseline before mutation.

## 2. Prepare narration and audition

Apply established wording and pronunciation rules to the spoken derivative, logging each change against its source and verse. Present unresolved meaning or wording choices in complete before/after sentences. Use the current approved pronunciation dictionary for both first generations and repairs.

A paid generation requires explicit authorization. Submit one take per authorized request; another take requires another explicit instruction. After an error or timeout, inspect provider request state before considering a retry. Keep the exact prompt, its hash, provider/model configuration and response provenance in private production records.

Keep unaccepted audio in temporary audition storage outside the persistent project and media library. Provide playback for review. Approval attaches to the selected reading or passage, including when one file contains multiple readings. Map and extract only accepted complete passages before promoting audio to production. An approved spelling, prompt or repair plan does not constitute listening approval.

## 3. Match words before locating cuts

Match the actual recited or narrated passage to the canonical Arabic and approved spoken translation. Identify first and last complete words, verse ownership, connected clauses and repetitions. Map each narration take independently.

Recognition can help identify words and broad context. Its timestamps must not set or rank cuts, speech endings, next attacks, tails or spacing anchors. Do not infer word ownership from detector regions, range labels, expected sequence or waveform shape. Investigate only the unresolved passage instead of repeating broad recognition over unchanged audio.

Decode each source once and reuse its measurements. The established candidate profiles are:

| Candidate setting | Recitation | Dry narration |
| --- | --- | --- |
| Speech threshold | 0.35 | 0.35 |
| Minimum speech / silence | 100 / 96 ms | 70 / 64 ms |
| Speech padding | 0 ms | 0 ms |
| Energy step | 5 ms | 2.5 ms |
| Preceding-minimum search | Up to 80 ms | Up to 80 ms |
| Earlier-only weak-attack refinement | 600 ms; fraction 0.04 | 600 ms; fraction 0.005 |

Recitation ending candidates use the recorded next-attack-constrained local relative-energy profile, with fraction 0.25. Narration uses its own local-floor/low-energy profile. These settings generate candidates; they cannot certify words or impose a universal minimum usable pause.

## 4. Review and save one source map

Inspect narrow uncut source context with full signed waveforms and the corresponding words. Verify the complete outgoing word through held vowels, consonant closures, internal pauses and resumed syllables. Independently identify the genuine next word and its first attack. A later isolated syllable can still belong to the outgoing word.

For every internal verse boundary in a proposed multi-verse group, record word ownership, source-specific evidence, the reviewed window, measured usable interval and the reason to join or split. A shared detector region is only a grouping proposal. Run the connected-group checker before compiling or assembling accepted groups. Its result does not certify individual or newly split word boundaries.

Save one reviewed map with source identity/hash, verse range, source and spoken text, word evidence, complete start/end, next attack, tail interval and explicit corrections. Cover all verses, repetitions and translated clauses in order. Keep unresolved candidates separate; ambiguity blocks dependent cuts and placement.

The tail is the entire source interval between the complete outgoing speech ending and the genuine next attack. There is no independent decay endpoint. Review end-of-file and different-source joins separately. Do not shorten a confirmed tail with an automatic frame guard.

## 5. Assemble from the reviewed map

Follow **find out → cut → place** using the approved native template: A1 recitation body, A2 translation and A3 recitation tail. Reuse accepted shared opening components and approved effects. Preserve original media, source handles, fractional offsets, existing markers and protected edits.

For this production profile, use a three-frame recitation entrance fade. Measure nine timeline frames from the main recitation clip's exclusive right edge to the translation's actual first audible attack, and six frames from the translation's exclusive right edge to the next recitation's attack. Compensate incoming quiet lead-in. Neither the tail endpoint nor its midpoint defines these gaps. At 24 fps, nine and six frames are 0.375 and 0.25 seconds respectively.

Prefer a verified native API for supported controls. Before moving following material, identify the exact objects and include each body with its matching tail. Verify actual position deltas after movement. After a timeout or partial mutation, read current state before retrying.

## 6. Verify the native result and listening state

Compare actual source offsets, record positions, complete words, pairing, gaps, fades and effects against the reviewed map and preserved baseline. For each body/tail pair, verify source-time alignment, intended overlap, paired fades, equal absolute clip Volume and equal movement. A matching plan alone does not prove these properties in the editor.

Retain the approved common narration Level and chain. Apply authorized recitation leveling per recording across its body/tail pairs, preserving established shared components. Set absolute clip Volume once; do not stack gain or normalize phrases individually.

Review advancing native playback and actual output for complete articulation, joins, incoming-word leakage, clipping, level and settled endings. Use native review by default; a diagnostic render is a separate scoped action. Meter readings cover only their measured windows. Technical checks do not replace human approval of the take or final listening.

## Evidence and completion

Keep these states separate in the production record:

| State | Required evidence |
| --- | --- |
| Prepared | Text, candidates or plan exist; no implementation implied |
| Source reviewed | Exact recording and complete-word boundary evidence are recorded |
| Take approved | A human selected the identified reading or passage |
| Placed | Native readback confirms the intended implementation |
| Technically verified | Source geometry, properties and actual output checks passed within the stated scope |
| Listening approved | A human accepted the audible result |

Record synchronization and publication separately. Report unavailable readbacks as unknown and preserve unresolved findings. Full source coverage, recognizer agreement, passing group validation and correct native geometry cannot independently establish complete phonemes or semantic correctness.
