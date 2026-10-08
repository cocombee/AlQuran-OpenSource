# Production rules

These are the current reusable rules for the [production workflow](production-workflow.md). Rule identifiers preserve continuity with the production method; they do not refer to bundled private histories. A new rule does not authorize a paid request, change existing audio or resume paused editing.

## Canonical text and spoken derivatives

Keep canonical Arabic, translation, footnotes and verse references unchanged. Maintain a separate narration derivative with a source-linked change log. Preserve speaker, meaning, meaningful pronouns and explicit addresses. Retain useful clarifiers; omit an explanatory gloss only when its redundancy is established in context. Brackets alone do not justify deletion or the insertion of a connector or pause.

Apply established rules consistently to first-generation prompts and repairs. Show only unresolved wording decisions for approval, using complete original and proposed sentences with stable review identifiers. Scope a correction to its approved construction; do not extend a single verse's wording change to unrelated passages.

### Source-following referential -nya — D136

When the following source-provided noun or phrase explicitly names the referent of **-nya**, use that noun or phrase directly in the spoken derivative. Review both bracketed explanations and ordinary source wording. Preserve the grammar of the complete construction without adding an unnecessary comma or connector.

Retain meaningful possession, agency, unglossed pronouns and nonreferential endings such as **sesungguhnya**. A nearby noun does not automatically establish the referent. Use the referent supplied by the approved source; do not invent one from memory or commentary. A construction-specific removal of a linking word is not a global deletion rule.

### Spoken pronunciation — D135 and related rules

For Indonesian narration, use the whole-word pronunciation adaptation **roh → ruh**, including **roh-roh → ruh-ruh**, preserving capitalization. Record the derivative while retaining the canonical spelling.

Use the current approved pronunciation dictionary and context-matched cues throughout every prompt. Verify each audible occurrence independently; correct input spelling or recognizer output does not prove successful pronunciation. Preserve natural pace and full voice. Improve articulation through complete consonants and appropriate vowels rather than increased intensity. Chapter endings should sound composed and settled; reset carried question cues locally without changing source meaning.

## Complete-word and internal-boundary review — D133–D134

Every cut must retain the complete outgoing word, including quiet internal breaks and resumed final syllables. Independently identify the next verse's actual first word and attack. This applies to single-verse and one-word rows as well as larger groups.

Only after word ownership is established, measure the usable interval between the complete ending and next attack. Record whether separation preserves both words and the approved body/tail treatment. A verified usable interval may permit a split even when voice activity detection merged the passage. Continuous delivery without a usable independent interval stays joined. Uncertain ownership or distance blocks dependent production.

Record a source-hash-specific review for every internal boundary of an accepted multi-verse group. A generic reviewed flag, waveform thickness, reverb energy or shared detector ID is insufficient. Split decisions must become separate mapped groups. Run the connected-group check before compilation and assembly, while retaining independent complete-word review for every resulting boundary.

Do not impose a universal silence minimum, add a separate decay detector, choose the nearest recognition timestamp or automatically subtract a lead/frame guard from a confirmed attack. Failed acoustic screening calls for closer word-context review; passing screening produces a candidate only.

## Audition storage, selection and numbering — D125

- Keep unaccepted and rejected audio only in temporary audition storage outside the persistent project and production media folders. Do not import it into the editing project.
- Promote only accepted audio. If a combined take is partly accepted, keep the mixed source temporary until accepted complete passages are independently mapped and extracted. A selected reading does not approve other readings in the same file.
- Keep the same repair number through unaccepted retries and partial approval of the same correction. Reserve established numbers and approved portions for accepted or partly accepted repairs. Assign a new number to a new correction after those reservations.
- Keep immutable prompt, request, hash and revision provenance separately in private records. Stable human-facing numbering must not overwrite that provenance.
- Inspect current native and shared-media dependencies before overwriting, moving or deleting an asset. Preserve pending auditions during listening. A retry number or filename does not authorize another paid generation.

## Preserve current native edits

Use the latest actual timeline as the baseline, including human corrections. Preserve outside source offsets, fractional positions, fades, absolute clip Volume, effects and markers. Do not restore stale plans over newer edits.

Verify body/tail source-time alignment, intended overlap, paired fades, equal absolute Volume and equal movement. A short verified tail may require shorter paired fades to preserve both complete words. Apply suitable numeric tolerance to fade readbacks; sub-sample rounding noise does not justify rebuilding audio.

Set absolute clip Volume instead of adding the same gain repeatedly. Preserve the approved common narration Level, recording-wide recitation Level and established shared components. A reference gain is not a universal gain for every source.

After a modal interruption, reconnect and confirm the actual editor state. An unavailable property is unknown, not zero. Read partial changes before retrying. Confirm playback through advancing transport and actual output; a checked playback control alone proves neither.

## Authorization and evidence limits

Paid generation, human take selection, native implementation, final listening and publication are distinct decisions. Respect the scope already authorized; request new authorization for additional paid takes or work outside that scope. Rule approval and technical success do not silently expand it.

Candidate generation, source coverage, broad recognition, absence of dropouts and correct body/tail geometry cannot certify semantic identity or complete terminal phonemes. A connected-group check validates its recorded evidence requirements, not the sound of every word. Describe checks by their actual scope and keep **prepared**, **placed**, **technically verified** and **human approved** separate.

Publish reusable source and instructions only after removing private account identifiers, credentials, media paths, provider receipts and production histories. These public rules include no approval for publishing recordings, licensed corpora or private project data.
