# How we work: branches, versions, releases

Valid for the six code repositories and for this one, from version 0.9.10 on.
Agents: read this before changing anything, and keep to it.

## Branches

| Branch | Holds | Protected |
|---|---|---|
| `main` | **the last released version, always** | yes, merge by maintainers only |
| `next` | development towards the next release | yes, merge by maintainers only |
| `feature/<name>`, `issue/<n>-<name>` | one feature or issue, cut from `next`, merged back into `next` by a merge request | no |
| `security/<name>` | a security patch, cut from **`main`** | no |

Tags `v*` are protected. Nobody pushes to `main` or `next` directly.

### Stable release (from `next` to `main`)

1. On `next`: bump versions and manuals (the files of each repository are listed in
   its `CLAUDE.md`), changelog entries, `docs/manual` changes in `activitytrack-doc`.
2. Merge request `next` → `main`, merged **fast-forward only** (no merge commit, no
   rebase). After it, `main` and `next` are the same commit.
3. Tag `vX.Y.Z` on `main`. The full pipeline runs on the owner's command, Windows jobs
   included (they are the only ones that run the packaged executables).
4. Right after the release, **merge `main` into `next`** (not a rebase: `next` is shared).
   It is a no-op except where CI commits to `main` after the tag (the app's
   `Update manifest for vX.Y.Z [skip ci]`); without it the next fast-forward is refused.

Order across repositories: library first (the cli, tui and desktop clone it at the tag
named in `.gitlab/lib-ref`), then cli, tui, desktop, web, app, and the documentation.

### Beta releases (from `next`)

- Tag `vX.Y.Z-beta-N` on `next`, with X.Y.Z the **next** version (`v0.9.10-beta-1`).
- The update checks treat any suffix as a pre-release: a beta is older than its release
  and is offered to those who asked for betas only.
- In Debian packages the version is written `X.Y.Z~betaN-1` (a hyphen in an upstream
  version sorts after the release, the tilde before it).
- Prerequisite: the unit tests and the **Wine** jobs of the local runner pass. The paid
  Windows pipeline is not required. The Windows executables of a beta are built under
  Wine and are **not started** there (Wine cannot run a PyInstaller bundle): the release
  notes say so.

### Security patches

- Branch `security/<name>` from `main`, label `security` on the issue (confidential
  until released) and on the merge request.
- Version: a fourth component, `X.Y.Z.1` (`v0.9.9.1`), so that it never collides with
  the number `next` is preparing. `0.9.9 < 0.9.9.1 < 0.9.10-beta-1 < 0.9.10`.
- Merge into `main`, tag, **release at once** with the security report attached to the
  release; then merge `main` into `next` (port the fix; resolve conflicts there).
- The report states: what, who is affected, since which version, the fix, the credit.

## Day to day

1. `git switch next && git pull`, then `git switch -c feature/<name>`.
2. Test locally first (see below), commit with a message that says why.
3. Merge request to `next`. The jobs tagged `local` run on the owner's runner (free);
   jobs on GitLab's shared runners and the Windows jobs run **only on command**.
4. A feature that changes behaviour also changes its manual: a second merge request in
   `activitytrack-doc`, to its `next`, linked from the first.

### Local tests (no CI)

- App: `./gradlew --offline -q :core:domain:test :core:data:testDebugUnitTest :app:compileDebugKotlin`
- Server: `manage.py test` in a Django 4.2 virtual environment.
- Python repositories: `python3 -m unittest discover -s tests -t .`
- Windows code paths: the `windows-wine` jobs on the local runner, then (before a stable
  release) the full Windows pipeline on the shared runners or on the owner's Windows 11 VM.

## Rules that do not bend

- Pipelines on GitLab's shared runners cost money: start one only when the owner says so.
- No secrets in repositories, merge requests, issues, logs or this documentation: they are public.
- The Android application id `it.infraconsulting.activitytrack`, the AppStream ids and
  the package names do not follow the GitLab group's name and never change.
- Commits end with the `Co-Authored-By:` line naming the model actually used.
