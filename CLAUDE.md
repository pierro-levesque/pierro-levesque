# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working on this repository.

## Repository Overview

This is a **GitHub personal profile repository** (`pierro-levesque/pierro-levesque`). GitHub treats a repository with the same name as its owner as a special profile repository — its `README.md` is displayed publicly on the owner's GitHub profile page.

## Repository Structure

```
pierro-levesque/
├── CLAUDE.md       # AI assistant guidance (this file)
├── LICENSE         # GNU General Public License v3
└── README.md       # GitHub profile page content (publicly visible)
```

## Files

### README.md
The primary content of this repository. Whatever is written here appears on the GitHub profile at `github.com/pierro-levesque`. It supports full GitHub-flavored Markdown (GFM), including:
- Badges (shields.io, GitHub stats widgets, etc.)
- Images and GIFs
- HTML elements (GitHub renders a safe subset)
- Collapsible `<details>` sections
- Tables

### LICENSE
GNU General Public License v3 (GPLv3). No changes should be made to this file.

## Development Workflow

This repository has no build process, dependencies, tests, or CI/CD pipeline. Changes involve editing Markdown files directly.

### Making Changes

1. Edit `README.md` to update the GitHub profile content.
2. Commit with a descriptive message (e.g., `Update README with current projects`).
3. Push to `master` — GitHub automatically renders the updated README on the profile page.

### Branch Strategy

- `master` — the default branch; GitHub reads `README.md` from this branch for profile display.
- Feature/editing branches (e.g., `claude/...`) should be merged into `master` when complete.

## Conventions

- **Markdown style**: Use standard GitHub-flavored Markdown. Keep lines readable (80–120 chars where practical).
- **No trailing whitespace** in Markdown files.
- **Emoji**: GitHub renders emoji shortcodes (`:wave:`) and Unicode emoji directly. Use sparingly and intentionally.
- **License**: Do not modify `LICENSE`.
- **No new binary or build files**: This repository is documentation-only.

## Common Tasks for AI Assistants

- **Update profile content**: Edit `README.md` with new information about the owner's current work, skills, or links.
- **Fix typos**: The current README contains a typo (`"Hi theres"` — should likely be `"Hi there"`).
- **Add badges or stats**: Integrate GitHub stats cards, language badges, or other profile widgets via Markdown image syntax.
- **Structure sections**: Organize the README into clear sections (About, Projects, Skills, Contact, etc.).

## Notes

- There is no `package.json`, test suite, linter, or formatter configured.
- The repository has two commits in its history: the initial commit and a README update.
- No CI/CD workflows exist under `.github/workflows/`.
