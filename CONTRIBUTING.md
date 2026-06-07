# Contributing

This project enforces commit message rules to keep history clear and consistent.

## Commit message format

Use the Conventional Commits style for the commit subject line (single-line):

type(optional-scope): short description

- `type` must be one of: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`
- `optional-scope` is a short label (no spaces) describing the area (e.g. `api`, `timer`).
- Keep the short description <= 50 characters.

Examples:

- `feat(api): add user authentication`
- `fix(timer): correct timezone handling`
- `docs: update README examples`

## Enabling git hooks

The repository includes a `commit-msg` hook in `.githooks/` that validates commit messages.
Enable it by running:

```sh
git config core.hooksPath .githooks
```

Alternatively run the installer script in `scripts/` for your platform:

```sh
sh scripts/install-git-hooks.sh
```

or on Windows PowerShell:

```powershell
.\scripts\install-git-hooks.ps1
```

If you cannot enable hooks, follow the format manually when writing commit messages.
