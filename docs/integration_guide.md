# 🔌 Integration Guide: Agent Skills, Claude Code, Antigravity & CI/CD

This guide walks through integrating **Precog Council** into your existing developer workflow across various environments.

---

## 1. Universal Agent Skill Installation (`gh skill` & `npx skills`)

Precog Council adheres to the open standard **Agent Skills specification** (`SKILL.md`). You can install it into any supported AI coding agent (Claude Code, Cursor, GitHub Copilot CLI, etc.) with a single command:

### Via GitHub CLI (`gh skill`)
```bash
# Global user-level installation
gh skill install <your-github-username>/precog-council --scope user

# Or project-scoped installation
gh skill install <your-github-username>/precog-council --scope project
```

### Via Vercel Labs Skills CLI (`npx skills`)
```bash
# Global installation
npx skills add <your-github-username>/precog-council -g

# Or local project installation
npx skills add <your-github-username>/precog-council
```

---

## 2. Claude Code Integration (`claude`)

### Option A: Custom Skill / Command
Precog Council comes pre-bundled with `.claude/skills/precog-council.md`.
To make it available globally across all your projects in Claude Code:

```bash
mkdir -p ~/.claude/skills
cp .claude/skills/precog-council.md ~/.claude/skills/
```

Inside any Claude Code session, simply prompt:
> *"Run precog council on this function"*  
> *"Arbitrate this proposal with precog council and show the minority report"*

### Option B: Bash Tool Execution
Claude Code can also directly invoke the CLI tool:
```bash
claude "Run 'uvx precog-council --file auth.py --domain code' and explain the minority report"
```

---

## 2. Google Antigravity Integration (`agy`)

### Project-Scoped Skill
Keep the skill in your project's `.agent/skills/precog-council/SKILL.md`.

### Global User Skill
To use Precog Council in any Antigravity workspace:
```bash
mkdir -p ~/.gemini/skills/precog-council
cp -r .agent/skills/precog-council/* ~/.gemini/skills/precog-council/
```

---

## 3. GitHub Actions PR Bot Integration

To automatically review every Pull Request in your repository:

1. Copy `.github/workflows/precog-review.yml` to your repository's `.github/workflows/` directory.
2. In your GitHub Repository Settings (`Settings -> Secrets and variables -> Actions`), add at least one of the following API keys as repository secrets:
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`
3. Ensure Workflow Permissions (`Settings -> Actions -> General -> Workflow permissions`) are set to:
   - **Read and write permissions** (needed for posting PR comments).
4. Now, every new Pull Request or commit push will automatically trigger a 3-Precog review, publishing the verdict and any **Minority Report** as a comment!
