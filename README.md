# 🏛️ Precog Council // Pre-Crime Decision Engine

> *"The Pre-Cogs are never wrong. But occasionally... they disagree."*  
> — *Philip K. Dick, Minority Report*

**Precog Council** is a multi-model arbitration framework and CLI tool that evaluates code, system architecture, quant features, or business decisions using **three independent analytical lenses (Precogs)** and critically isolates the **Minority Report (1-of-3 dissent)** to expose fatal blind spots.

---

## 💡 Why Precog Council?

Traditional LLM ensembles and Mixture-of-Agents (MoA) naively seek **majority consensus**, averaging out dissent. But in mission-critical systems—such as quantitative trading, cybersecurity, or core infrastructure—disasters rarely occur from common consensus; **they occur in the blind spot that only one dissenting model noticed**.

When a 2-vs-1 split occurs, **Precog Council elevates the minority dissent as a first-class warning alert**, giving humans the exact counter-evidence needed before catastrophic deployment.

```
       [ Proposal / PR Diff / Strategy ]
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  [ Agatha ]      [ Arthur ]      [ Dashiell ]
  Efficiency &    Adversarial     Occam's Razor
  Scalability     Risk Auditor    & Simplicity
       │               │               │
       └───────────────┼───────────────┘
                       ▼
              [ Council Verdict ]
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   【3 vs 0 Unanimous】        【2 vs 1 Split】
   High-Confidence Pass       Majority Adopted, but
                              🚨 MINORITY REPORT EXPOSED
                              (Critical Risk Warnings)
```

---

## 👥 The Three Precogs

| Precog | Default Role (Code Domain) | Analytical Focus |
| :--- | :--- | :--- |
| **Agatha** | **Algorithm & Efficiency** | Time/space complexity $O(N)$, concurrency, scale, and mathematical rigor. |
| **Arthur** | **Adversarial Risk Auditor** | Edge cases, vulnerabilities, data leakage, boundary collapse, silent failure. |
| **Dashiell** | **Occam's Razor & Clean Code** | Parsimony, readability, YAGNI, eliminating over-engineering and cognitive bloat. |

---

## 🚀 Quick Start (Zero-Friction)

### Run Instantly with `uvx` (No Installation Required)

```bash
# Code review of a diff or function
uvx precog-council "Refactor user authentication loop" --context "def login(): ..." --domain code

# Review a file directly
uvx precog-council "Database Migration" --file schema.sql --domain architecture

# Quant feature evaluation
uvx precog-council "Signed Path Efficiency" --file feature.py --domain feature
```

### Install via pip or uv

```bash
uv tool install precog-council
# or
pip install precog-council
```

---

## 🎯 Domain Presets

Precog Council comes preloaded with tailored analytical roles for different domains (`--domain <name>`):

* **`code`**: Algorithm Efficiency vs. Security/Edge Cases vs. Maintainability & Simplicity
* **`architecture`**: Scalability & Extensibility vs. Fault-Tolerance/SPOF vs. Operational Cost/Simplicity
* **`business`**: Market Upside & Opportunity vs. Downside & Legal/Financial Risk vs. Lean Velocity
* **`feature`**: Market Microstructure & Causality vs. Forward Leakage (`shift(1)`) vs. Noise Filter
* **`general`**: Strategic Vision vs. Devil's Advocate vs. Pragmatic Realism

---

## 🛠️ Cross-Platform Support: Claude & Antigravity

Precog Council automatically detects your environment:

1. **Direct API**: Uses `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY` directly.
2. **Claude Code (`claude`)**: Works natively within Claude Code sessions via `claude -p` or `.claude/skills/precog-council.md`.
3. **Antigravity CLI (`agy`)**: Works seamlessly in Google Antigravity workspaces via `agy -p`.

---

## ⚙️ Repository Configuration (`precog.yaml`)

Place `precog.yaml` in your repository root to enforce team-specific audit rules and **Veto power**:

```yaml
domain: code
backend: auto
default_model: inherit

# Custom roles tailored to your stack:
precogs:
  agatha: "Distributed Concurrency in Go"
  arthur: "Zero-Trust Security & OWASP Top 10"
  dashiell: "Go Idiomatic Minimalism & Readability"

# VETO: Overrides majority vote to REJECT if this role dissents!
veto_roles:
  - "Zero-Trust Security & OWASP Top 10"
```

---

## 🤖 GitHub Actions CI/CD Integration

Automate 3-Precog pull request reviews by adding `.github/workflows/precog-review.yml`:

```yaml
name: Precog Council PR Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: |
          git diff origin/${{ github.base_ref }}...HEAD > diff.txt
          uvx precog-council "PR Review" --file diff.txt --domain code --format markdown > report.md
      # Post report.md back to PR comment!
```

---

## 📄 License

MIT License. Built for rigorous engineering teams that refuse to be blinded by false consensus.
