# Architecture

AlQuran is a local production pipeline with explicit human review steps. The public repository contains reusable tools and the rules for using them; it does not contain a hosted listening service.

```mermaid
flowchart LR
    S[Licensed source text and recordings] --> P[Approved narration prompt]
    P --> A[One authorized audition]
    A --> H[Human listening and selection]
    S --> W[Word and waveform review]
    H --> W
    W --> M[Verified source map]
    M --> R[Approved Resolve edits]
    R --> V[Native playback and final review]
    V --> E[Approved edition]
```

## Module ownership

| Area | Responsibility | Boundary |
| --- | --- | --- |
| Narration client | Explicit service requests and local provenance receipts | No automatic retries, take approval or timeline edits |
| Speech analysis | Word-identity evidence and candidate analysis windows | Does not certify complete words or edit boundaries |
| Review utilities | Connected-group evidence checks and waveform views | Human approval remains separate from validation |
| Resolve transport | One request to a locally installed MCP process | Caller must authorize and verify any native mutation |
| Production documents | Source, audition, boundary and acceptance rules | Do not replace source permissions or listening review |

## Data and configuration

Credentials and voice selection come from local configuration. Source media, canonical translations, prompt text, receipts and native timeline records remain in private local storage. Public tests use synthetic data.

An audition receipt records the prompt hash, model and voice selection, request metadata and returned audio hash. Its approval state starts as pending. Output files must be outside the repository and must not already exist. Only a selected accepted reading is promoted to persistent production storage.

Recognition emits word-identity evidence. Candidate analysis windows are expressed as start/end seconds. Connected-group validation checks that boundary evidence exists; it cannot determine whether that evidence is semantically correct.

## Failure and recovery

A failed or ambiguous paid request is inspected in the service's request log before an explicitly authorized retry. Existing outputs are preserved. Native timeline edits require a saved before-state, a bounded intended change and readback/playback verification. Documentation or offline tests never mutate an active project.

## Integration limits

The Resolve transport currently uses POSIX pipe polling and is intended for macOS/Linux. Speech tools require local model/dependency installation. The tools are separate command-line utilities; an integrated application and public listening interface remain roadmap work.
