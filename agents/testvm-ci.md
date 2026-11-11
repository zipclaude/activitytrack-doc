# GitLab runner on the test VM (tag `testvm`)

For agents (and people) working on this machine. Not part of any repository.
Complements `local-ci.md` (the runner on the owner's machine, tag `local`), which
stays as it is. Read `workflow.md` first: pipelines are started only on the
owner's word, and shared runners cost money.

## What it is

- Project runner `testvm (owner's test VM)` (id 58990830), tag `testvm`,
  **does not run untagged jobs**, **not protected** (it runs any branch),
  not locked. Created in the app project and enabled for the app, web, library,
  cli, tui, desktop and doc projects. (A Maintainer cannot create a group
  runner; a new project has to be added with
  `POST /projects/:id/runners` `runner_id=58990830`.)
- On the test VM (Debian 13): `docker.io` (data-root `/srv/docker`) and
  `gitlab-runner` from the official GitLab apt repository, both enabled at
  boot as systemd services. Runner configuration `/etc/gitlab-runner/config.toml`
  (holds the runner token: never print or copy it), `concurrent = 4`,
  executor docker, `privileged = false`, `pull_policy = ["if-not-present"]`.
- Everything the runner stores is on the dedicated volume `/srv` (the root
  file system is small): builds `/srv/gitlab-runner/builds`, cache
  `/srv/gitlab-runner/cache`, Gradle home `/srv/gitlab-runner/gradle`
  (mounted as `/root/.gradle` in every job, so dependencies are downloaded once).
- The test install of activitytrack-web on the same VM is untouched.

## Images (built by hand on the VM, kept there)

Dockerfiles in `testvm/` next to this file (the build commands are in their
first lines). Jobs use them as `image:`; with `if-not-present` they are never
pulled from a registry, so rebuild one on the VM when its contents must change.

| Image | For |
|---|---|
| `activitytrack/android:37` | JDK 21, Android cmdline-tools, platform 37, build-tools 36.0.0 (`ANDROID_HOME=/opt/android-sdk`) |
| `activitytrack/pytest:trixie` | Debian trixie with git, Python, Django 4.2, segno, argon2, psycopg, cryptography, keyring, PyQt6, dbus, flake8, gettext |
| `debian:trixie`, `debian:trixie-slim` | pre-pulled |

## The jobs

Each of the six code repositories has a job `testvm` (tag `testvm`) on the
branch `feature/activity-1.0` and, when it is merged, on later branches:

- app: `./gradlew --no-daemon :core:domain:test :core:data:testDebugUnitTest :app:compileDebugKotlin`
- web: `manage.py check`, `makemigrations --check`, `manage.py test` (SQLite only,
  Django from trixie; the PostgreSQL variant is not run here)
- library: flake8, `scripts/strings.py --check`, `python3 -m unittest discover -s tests -t .`
- cli, tui, desktop: the same, with the library cloned at the branch of the
  variable `TESTVM_LIB_REF` (default `feature/activity-1.0`) instead of the tag
  of `.gitlab/lib-ref`. Change it in the job when the library moves.

**Selection.** The `testvm` job runs only when the pipeline has the variable
`TESTVM` or its branch is named `testvm/<anything>`; every other job has that
condition first in its rules with `when: never`. So such a pipeline contains the
`testvm` job and nothing else, and without it nothing changes.

## Starting a pipeline (needs the owner's go-ahead, see workflow.md)

The projects forbid pipeline variables (`ci_pipeline_variables_minimum_override_role`
is `no_one_allowed`; do not change it), so `TESTVM=1` is refused by the API. Use a
branch named `testvm/...` instead:

```
git push origin <branch>:refs/heads/testvm/<name>     # a push starts no pipeline
curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/<id>/pipeline?ref=testvm/<name>"
# right after: the jobs must all have tag testvm, otherwise cancel at once
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>/jobs"
curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>/cancel"
```

Where variables are allowed, `variables[][key]=TESTVM&variables[][value]=1` on any
ref does the same. The branch `testvm/activity-1.0` exists in the six repositories
(same commit as `feature/activity-1.0`; move it with a forced push when needed,
delete it when it is no longer useful). Check a change of the CI file first with
the lint API (`POST /projects/:id/ci/lint`, `dry_run`, `include_jobs`): its pipeline
must have no workflow-blocked error and only `testvm` jobs. A merge request into
`next` still runs the old `local` jobs only; the `testvm` job never runs there.

## Operating

On the VM, as a user with sudo:

```
systemctl status gitlab-runner docker     # both start at boot
sudo systemctl stop gitlab-runner         # stop taking jobs (start: same with start)
sudo journalctl -u gitlab-runner -f       # log
sudo gitlab-runner verify                 # token still valid?
docker system df                          # disk; "docker system prune -f" frees dangling data
df -h /srv                                # 18 GB volume
```
Online state: Settings → CI/CD → Runners of any of the projects, or
`GET /runners/58990830` (`status`).

## Limits

- 16 CPU, 8 GB RAM shared by up to 4 jobs and by the web test install; Gradle runs
  with `--no-daemon`. Do not raise `concurrent` for the app job.
- No Windows or Wine jobs, no `docker build` in jobs (no privileged mode), no
  `services:` verified.
- The runner is not protected: it runs jobs of any branch of the seven projects,
  so keep secrets out of those projects' unprotected variables and files.
- Images exist only on this VM: the `testvm` jobs fail elsewhere.
- Verified 2026-11-11: the `testvm` job of each of the six repositories ran to
  success on `testvm/activity-1.0` (see git log for the commit tested).
