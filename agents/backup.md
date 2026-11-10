# Backup of the GitLab group (on demand)

`scripts/gitlab-backup.py` saves everything the group `activitytrack` holds into a
dated directory. Standard library and `git` only; nothing is installed on GitLab.

```sh
scripts/gitlab-backup.py --list                    # which projects it would save
scripts/gitlab-backup.py --out ~/gitlab-backups     # all of them (about 600 MB today)
scripts/gitlab-backup.py --only activitytrack-cli   # one project
scripts/gitlab-backup.py --owned                    # plus the projects owned by the token's user
scripts/gitlab-backup.py --no-packages --no-export  # code and JSON only (fast)
```

The token comes from `$GITLAB_TOKEN` or `~/API-keys/gitlab-token.txt`: scope `api`, role
Maintainer on the projects. It is never printed, never on a command line, never saved.

## What a backup holds

Per project: `repo.git` and `repo.bundle` (all branches and tags), `wiki.git`,
`export.tar.gz` (GitLab's own export: issues, merge requests with discussions and refs, labels,
releases, pipelines' metadata, settings), `json/` (the same as plain JSON), `packages/` (the
release files of the package registry), `variables.keys.json` (names and flags only). At the top:
`SHA256SUMS`, `backup.json` (counts and errors), `_groups/` (group data, members, labels).
Check it with `cd <backup> && sha256sum -c SHA256SUMS --quiet` (it covers `backup.json` too).
Secrets GitLab puts in its records (`runners_token` and the like) are removed from the JSON.
Exit code: 0 complete, 1 a step failed (`backup.json` says which), 2 complete but some parts were
refused or unsupported (`skipped` in `backup.json`).

## What it does NOT hold (keep it where it was created)

- The **values** of the CI/CD variables: among them the Android release keystore and its
  passwords. Without the keystore no update of the app can be signed: keep a copy
  of it encrypted and outside GitLab.
- Job artifacts (they expire), runners, access tokens, the group export (needs the Owner role:
  Group > Settings > General > Advanced > Export group, by the owner).

## Restoring

`export.tar.gz`: *New project > Import project > GitLab export*. `repo.bundle`:
`git clone repo.bundle name`. Packages: upload again with the generic package API.

## Keeping it

A backup is only worth something outside the machine and the account it protects. Encrypt it
before it leaves the machine (`tar c <dir> | gpg -c > backup.tar.gpg`), store at least one copy
offline, and run the script after every release (`scripts/gitlab-backup.py`, then `sha256sum -c`).
