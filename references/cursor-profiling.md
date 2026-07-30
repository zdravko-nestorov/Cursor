# Profiling & Performance in Cursor

## The one idea
Cursor does **not** ship a built-in APM/profiler like IntelliJ. It's a VS Code-based editor, so you use your stack's normal profiler. Cursor's value is the **AI loop on top**: attach the profile output to chat and let Agent interpret it, propose fixes, edit code, and re-run — a **measure → change → measure** cycle.

## Why this framing
Profiling tools measure; they don't fix. The slow part is usually the human reading a flamegraph, forming a hypothesis, editing, and re-measuring. That loop is exactly what an agent can drive.

## Step 1 — Profile with your stack's tooling
Use the standard profiler for your language, directly or via a VS Code extension:

| Stack | Typical profiler |
|-------|------------------|
| Node/JS | `node --prof`, Chrome DevTools, `clinic`, `0x` (flamegraphs) |
| Python | `cProfile` + `snakeviz`, `py-spy`, `scalene` |
| JVM (Java/Kotlin) | async-profiler, JFR (Java Flight Recorder), VisualVM |
| Go | `pprof` |
| Rust | `perf` + flamegraph, `cargo flamegraph` |
| Browser/Web | Chrome DevTools Performance panel; Lighthouse for Web Vitals |

Produce an artifact: a flamegraph, `pprof`/JFR file, `cProfile` dump, or the profiler's text summary.

## Step 2 — Hand the trace to Agent
Attach the artifact (or paste the top hot frames / the flamegraph screenshot) to chat and state the goal:

> "Here's the py-spy flamegraph for the `/report` endpoint. p95 is 1.8s; target <500ms. Find the hotspots and propose fixes."

Agent interprets the trace, identifies hotspots (N+1 queries, needless allocations, blocking I/O, bad algorithmic complexity), and proposes concrete edits.

## Step 3 — Change, then re-measure
1. Apply the change (Agent mode).
2. **Re-run the profiler** the same way.
3. Compare before/after numbers. Keep the win or revert and try the next hypothesis.
4. Repeat until the target is met.

```
measure ──▶ attach trace to Agent ──▶ apply fix ──▶ measure again
   ▲                                                      │
   └──────────────── compare & iterate ◀─────────────────┘
```

## Make it rigorous
- **Set a target first** (e.g. "p95 < 500ms", "LCP < 2.5s"). Optimize against a number, not a vibe.
- **Measure one change at a time** so you know what moved the needle.
- **Profile realistic scenarios** (prod-like data/load), not toy inputs.
- Pair with the `performance-optimization` skill (measure first; optimize only what matters) and `references/performance-checklist.md`.

## Anti-patterns
- Guessing at "slow" code and optimizing without a profile.
- Micro-optimizing a cold path while a hot query dominates.
- Changing several things at once, then not knowing which helped.
