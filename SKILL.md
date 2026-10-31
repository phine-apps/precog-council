---
name: precog-council
description: |
  Evaluates features, code diffs, architecture designs, or business proposals through a 3-Precog Council (Agatha, Arthur, Dashiell) with distinct analytical lenses, producing a majority consensus and isolating minority dissent.
  Use when asked to evaluate trade-offs, review complex changes, run arbitration, or "run precog council".
compatibility: "Requires Python 3.10+, uv or uvx"
allowed-tools: "Bash(uvx:*,precog:*,precog-council:*,python:*,claude:*,agy:*)"
metadata:
  version: "0.1.0"
  author: "phine-apps"
---

# 🏛️ Precog Council // Pre-Crime Decision Engine

Inspired by Philip K. Dick's *Minority Report*, this skill evaluates complex decisions by querying **three distinct analytical lenses independently**, producing a majority verdict while critically elevating the **Minority Report (1-of-3 dissent)** to expose fatal blind spots.

---

## 👥 The Three Precogs & Their Specialized Lenses

| Precog | Default Role (Code Domain) | Analytical Focus |
| :--- | :--- | :--- |
| **Agatha** | **Algorithm & Computational Efficiency** | Time/space complexity $O(N)$, concurrency, scale, and mathematical rigor. |
| **Arthur** | **Adversarial Security & Robustness Auditor** | Edge cases, vulnerabilities, data leakage, boundary collapse, silent failure. |
| **Dashiell** | **Occam's Razor & Idiomatic Maintainability** | Parsimony, readability, YAGNI, eliminating over-engineering and cognitive bloat. |

---

## 🚀 Execution Instructions for the AI Agent

When activated, you can execute the council in one of two modes:

### Mode 1: Automated Execution via CLI (Preferred if bash tool is available)

Run the pre-crime engine using `uvx` (zero installation) or the local `precog` CLI:

```bash
# Evaluate code changes or diff
uvx precog-council "Topic or PR Summary" --context "Inline diff or code snippet" --domain code

# Evaluate from file
uvx precog-council "Topic" --file path/to/file --domain architecture

# Generate clean Markdown for PRs or reports
uvx precog-council "Topic" --file diff.txt --domain code --format markdown
```

### Mode 2: In-Context Persona Triangulation (Native Fallback)

If bash execution is unavailable, simulate the 3-Precog arbitration directly in your reasoning:

1. **Phase 1: Agatha** independently evaluates from an efficiency/algorithmic lens.
2. **Phase 2: Arthur** independently hunts for vulnerabilities, edge cases, and failure modes.
3. **Phase 3: Dashiell** strictly enforces Occam's razor, maintainability, and simplicity.
4. **Phase 4: Synthesis & Minority Report**:
   - Aggregate the votes (`ADOPT` or `REJECT`) with confidence scores (0.0 to 1.0).
   - If split 2 vs 1: Highlight **🚨 MINORITY REPORT DETECTED 🚨** prominently, detailing the dissenting precog's exact risk warnings before giving the final recommendation.
