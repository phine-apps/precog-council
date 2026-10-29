# Contributing to Precog Council

Thank you for your interest in contributing to **Precog Council**! We welcome bug fixes, documentation improvements, new domain presets, and additional backend integrations.

---

## 🛠️ Local Development Setup

We use [`uv`](https://docs.astral.sh/uv/) for fast, reproducible dependency management and tooling.

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/precog-council.git
cd precog-council
```

### 2. Set up the environment
```bash
uv sync
```

### 3. Run the test suite
```bash
uv run pytest
```

### 4. Run linter and code formatting
```bash
uv run ruff check .
uv run ruff format .
```

---

## 🏛️ Adding a New Domain Preset

If you want to contribute a new domain preset (e.g., `legal`, `medical`, `game-design`):

1. Edit `src/precog_council/domains.py` and define three distinct, orthogonal analytical lenses (Agatha, Arthur, Dashiell).
2. Add corresponding test cases in `tests/test_domains.py`.
3. Update `README.md` to document the new domain.

---

## 🚀 Pull Request Guidelines

1. **Keep it atomic**: One feature, bug fix, or domain preset per PR.
2. **Include tests**: Add unit tests in `tests/` covering new logic or regression cases.
3. **Ensure CI passes**: Run `uv run pytest` and `uv run ruff check .` before pushing.
4. **No secrets or private paths**: Ensure diffs contain no API tokens, local absolute paths, or personal credentials.
