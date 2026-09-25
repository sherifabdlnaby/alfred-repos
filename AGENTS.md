# AGENTS.md

## Toolchain (mise)

This project uses [**mise**](https://mise.jdx.dev) to pin tools, expose tasks, and wire git hooks. `mise.toml` is the source of truth. Don't install tools by hand or add ad-hoc scripts; add a mise tool or task instead.

**Setup** (once, and per new worktree): `mise trust && mise run setup`.

**Run via mise.** Run `mise run check` before you call work done. A few examples, not the full list:

```sh
mise run check          # all linters/formatters/validators (alias: lint); add --fix to auto-fix
mise run build          # vendor deps into src/ and zip the .alfredworkflow (--version stamps info.plist)
mise run test           # tests (placeholder — none yet)
mise tasks              # discover every task
mise run <task> --help  # a task's flags
```

Prefer `mise run <task>` over calling the tool directly, so local, hooks, and CI stay in sync.

## Git hooks (hk)

`mise run setup` installs the hooks (on Git 2.54+ they live in git config, so an empty `.git/hooks/` does not mean no hooks). Commits run the [hk](https://hk.jdx.dev) commit gates on staged files, and a push runs the push gates; CI runs both as `mise run check`, so a green commit is not yet a green CI. Fix failures with `mise run check --fix`. For a shorter loop, target steps with `mise run check --step <name>` or skip them with `--skip-step <name>`. Don't disable steps to push a commit through; `git commit --no-verify` skips hooks for a WIP commit.

## Releases

Merging to `main` with a bump label (`major` / `minor` / `patch`) tags, builds the `.alfredworkflow`, attests provenance, and publishes a GitHub Release. Use `skip-release` when the change should not cut a version. Category labels (`feature`, `bug`, `docs`, `ci`, …) only group the generated notes. Manual RC: Actions → Release → `prerelease: true`.

## Project notes

- `src/` holds the workflow source (`repos.py`, `update.py`, `info.plist`) **and** vendored third-party deps (`workflow/`, `docopt.py`, `*.dist-info/`) that `mise run build` installs into it. The vendored paths are gitignored and excluded from linting (see `.config/hk.pkl`'s `commonIgnores`); never edit or lint them.
- `info.plist` carries a placeholder version (`1.3.37`). `mise run build --version vX.Y.Z` stamps the real version into a throwaway copy at build time, then restores the placeholder. Git tags are the source of truth for shipped versions (`pyproject.toml` version is informational only).
- `mise run clean` removes `build/` and the vendored deps from `src/`.

## Extending the setup

Changing tools, tasks, env, mise hooks, or pre-commit hooks? Edit the config, don't bolt on scripts, then run `mise run check`. Where things live:

- **`mise.toml`**: the source of truth for `[tools]`, `[tasks]`, `[env]`/`[vars]`, `[settings]`, `[hooks]`, and prerequisite `[doctor.checks]`.
- **`mise.lock`**: resolved versions plus checksums for every platform. Commit it; regenerate with `mise lock` after a `[tools]` change.
- **`.config/mise/`**: project-local state, like the gitignored setup stamp the `setup`/`enter` hooks read. File tasks (for logic longer than a few lines) live in `.config/mise/tasks/`.
- **`.config/hk.pkl`**: the pre-commit and `check` pipeline (linters and formatters, in Pkl). Add or edit a lint step here, in the commit or push tier; linter configs live beside it in `.config/` (zizmor's stays at `.github/zizmor.yml`).

For tool, task, and hook syntax, see the [mise](https://mise.jdx.dev) and [hk](https://hk.jdx.dev) docs.
