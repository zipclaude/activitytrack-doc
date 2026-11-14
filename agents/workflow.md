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
2. Merge request `next` → `main`, merged **fast-forward only** (the projects have the
   merge method `ff`: no merge commit; every merge request is rebased before it is merged). After it, `main` and `next` are the same commit.
3. Tag `vX.Y.Z` on `main`. The full pipeline runs on the owner's command, Windows jobs
   included (on a stable tag, GitLab's own paid Windows runners start the packaged executables;
   a pre-release has them tried on GitHub, see below).
4. Right after the release, **merge `main` into `next`** (not a rebase: `next` is shared).
   It is a no-op except where CI commits to `main` after a tag, beta or stable (the app's
   `Update manifest for vX.Y.Z [skip ci]`, the file the installed apps read at
   `raw/main/update-manifest.json`); without it the next fast-forward is refused. Do the same
   before opening the `next` → `main` merge request.
   The projects merge by fast-forward, so a merge request `main` → `next` cannot be merged
   (GitLab would have to rebase `main`). Use a sync branch instead:
   `git switch -c sync/main-into-next origin/next && git merge origin/main`, push it and open the
   merge request into `next`: it fast-forwards, because the branch is `next` plus the merge.

Order across repositories: library first (the cli, tui and desktop clone it at the tag
named in `.gitlab/lib-ref`), then cli, tui, desktop, web, app, and the documentation.

### Beta releases (from `next`)

- Tag `vX.Y.Z-beta-N` on `next`, with X.Y.Z the **next** version (`v0.9.10-beta-1`).
- The update checks treat any suffix as a pre-release: a beta is older than its release
  and is offered to those who asked for betas only.
- In Debian packages the version is written `X.Y.Z~beta-N-1`: the CI turns the tag's first hyphen
  into a tilde (a hyphen would sort after the release, the tilde before it) and the changelog adds
  the Debian revision `-1`.
- Prerequisite: the unit tests and the **Wine** tests (`windows-wine`) of the owner's runner pass.
  The paid Windows runners of GitLab are not used: the real Windows jobs of a pre-release (any
  suffix: `-alfa-N`, `-beta-N`) run on **GitHub**, free (activitytrack/activitytrack-doc#1):
  1. The tag is pushed on GitLab; the push mirror brings it to the GitHub backup in seconds, and
     there the workflow starts by itself (`on: push: tags: ["v*-*"]`, from the tagged commit's
     file). It runs the Windows tests, the real `windows-exe` of cli and tui (built and started)
     and the desktop's `windows-installer` (installed, tried, uninstalled), and, when everything
     is green, publishes the GitHub pre-release with all the files and `SHA256SUMS`.
  2. The GitLab tag pipeline (started by hand, as always) has the job `windows-github` (stage
     package, starts at once): `.gitlab/github-windows-gate.sh` polls the public GitHub API
     without a token for the run of the tag's commit, fails if it is red or does not appear
     within 15 minutes (the message says where to look), and downloads the Windows files of the
     GitHub release, checked against its `SHA256SUMS`.
  3. GitLab's `release` (next stage) publishes them under the same names as a stable release
     (`…-windows.zip`, `ActivityTrackDesktop-…-setup.exe`), so the app's manifest gets
     `cli-windows`, `tui-windows` and `desktop-windows` for pre-releases too. The library has no
     Windows file: there the job is only the gate.
  Re-running a GitLab pipeline after GitHub finished passes at once; a GitHub re-run replaces
  the files of its release. Nothing to configure: an optional masked project variable
  `GITHUB_TOKEN_RO` (a read-only token) only raises GitHub's limit of 60 requests/hour per IP.
  **GitHub down**: a maintainer sets the project variable `WINDOWS_GATE=skip` (Settings → CI/CD
  → Variables; pipeline variables are refused in these projects), runs the tag pipeline again and
  removes the variable. cli and tui then take the old Wine executable (`windows-wine-exe`, built,
  **not started**: Wine cannot run a PyInstaller bundle), the desktop goes without the installer,
  and the notes of each release say the Windows check was skipped.
- Stable tags are unchanged: GitLab's own paid Windows jobs. The same gate could replace them:
  widen the GitHub trigger to every `v*` tag, run `windows-github` on stable tags too and drop
  (or put behind a variable) `windows`, `windows-exe` and `windows-installer` in the four
  `.gitlab-ci.yml`. To weigh first: the backup would then publish its GitHub release before
  GitLab's, the stable release would depend on GitHub's availability (the `WINDOWS_GATE=skip`
  fallback would ship an untried Wine build), and both run Windows Server, not the users'
  Windows 11 (see `windows-runner.md`).

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
3. Merge request to `next`. Its pipeline runs the test job on the owner's runner (free: tag
   `local`); packaging, the Windows jobs and anything on GitLab's shared runners run **only on
   command**. Duo reviews the merge request: fix what it finds, it blocks the merge until then.
4. A feature that changes behaviour also changes its manual: a second merge request in
   `activitytrack-doc`, to its `next`, linked from the first.

### Local tests (no CI)

- App: `./gradlew --offline -q :core:domain:test :core:data:testDebugUnitTest :app:compileDebugKotlin`
- Server: `manage.py test` in a Django 4.2 virtual environment.
- Python repositories: `python3 -m unittest discover -s tests -t .`
- Windows code paths: the `windows-wine` jobs on the local runner, or a push of a branch
  `ghtest/<name>` to the GitHub backup (real Windows, free, no tag needed); before a stable
  release, the full Windows pipeline on the shared runners or on the owner's Windows 11 VM.

## Rules that do not bend

- Pipelines on GitLab's shared runners cost money: start one only when the owner says so.
- No secrets in repositories, merge requests, issues, logs or this documentation: they are public.
- The Android application id `it.infraconsulting.activitytrack`, the AppStream ids and
  the package names do not follow the GitLab group's name and never change.
- Commits end with the `Co-Authored-By:` line naming the model actually used.
