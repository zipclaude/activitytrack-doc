# Local GitLab runner for the ActivityTrack repositories

For agents (and people) working on this machine. Not part of any repository:
it names local paths.

## Rules

- **Pipelines on gitlab.com never start on their own** (since the `ci-manual-start`
  merge requests): the six `.gitlab-ci.yml` accept only `web` and `api` sources.
  Start one only when the owner asks, and only before a release. Never push a
  tag "to see what happens": a tag no longer starts anything, but it publishes
  a version name.
- Shared-runner minutes are paid for. A job without `tags: [local]` runs on the
  SaaS runners and costs credits.
- Day-to-day checks run **locally, without CI** (see "Quick loop").
- No secrets in jobs, logs or files of the repositories (they are public).
  Signing keys are protected CI variables of the app project: they reach
  protected refs only.

## The runner

- Group runner `zipclaude` (id 58715863) of `gitlab.com/activitytrack`,
  tag `local`, **does not run untagged jobs**, **protected** (runs jobs of
  protected branches and tags only, i.e. `main` and `v*`), `concurrent = 8`.
- Executor docker on **rootless podman**; the host is an LXC container without
  a logind session, hence the unusual setup:
  - everything needs `XDG_RUNTIME_DIR=/tmp/user/1000` (`/run/user/1000` does
    not exist; `/tmp` is cleared at reboot, the start script recreates it);
  - `pid_mode = "host"` in `~/.gitlab-runner/config.toml` (a new `/proc` cannot
    be mounted here); each job has its own network (slirp4netns over the
    `/dev/net/tun` the owner passed through);
  - `~/.config/containers/containers.conf` sets `default_sysctls = []`
    (`/proc/sys` is read-only) and `default_rootless_network_cmd = "slirp4netns"`
    (podman 5 wants `pasta`, not installed);
  - `containers.conf` also sets `netns = "slirp4netns"` and `pidns = "host"`, so
    containers that name no network (e.g. the runner's cache-permission helper)
    do not fall back to a bridge or a private `/proc`;
  - do NOT set `network_mode` in `config.toml`: the runner then sends a
    network endpoint config that podman refuses unless the mode is a bridge
    ("networks ... can only be used with Bridge mode"). The default
    `netns = "slirp4netns"` above does the job; each job has a private NAT
    network, and `services:` linked by name do not work with it (verify before
    relying on them);
  - images and layers live in `~/.local/share/containers` (30 GB, btrfs zstd).
- Binary `~/.local/bin/gitlab-runner`, start script `~/.local/bin/ci-runner`,
  log `~/.gitlab-runner/runner.log`, configuration `~/.gitlab-runner/config.toml`
  (holds the runner token: never print or copy it).

```
# start (detached) and check
setsid nohup ~/.local/bin/ci-runner > ~/.gitlab-runner/runner.log 2>&1 < /dev/null &
pgrep -a gitlab-runner
tail -f ~/.gitlab-runner/runner.log          # "Checking for jobs... nothing" = idle and healthy

# stop
pkill -f 'gitlab-runner run'; pkill -f 'podman system service'

# disk
podman system df ; podman system prune -af   # when the 30 GB fill up
```

The runner is started on request and stopped when not needed; it is not a
service. Check with `pgrep` before assuming it is running.

## Using it from a job

A job goes to this runner when it has `tags: [local]` **and** its ref is
protected. In the `.gitlab-ci.yml` of a repository:

```yaml
unit-tests:
  tags: [local]
  image: debian:trixie-slim      # any image reachable from docker.io; the default is debian:trixie-slim
  script:
    - ...
```

Limits of this runner: no Windows jobs, no `docker build`/DinD (no privileged
mode), one job at a time, `--pid host` (a job sees the host processes). Jobs
that need a service (PostgreSQL) use `services:` as usual; verify each one.

## Starting a pipeline on demand (needs the owner's go-ahead)

```
export GITLAB_TOKEN=...      # a token of your own (never echoed, never committed)
curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/<id>/pipeline?ref=<branch-or-tag>"   # source = api
# status / cancel
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>"
curl -s -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>/cancel"
```

Project ids: app 88636043, web 88639123, lib 88639115, cli 88639128,
tui 88639133, desktop 88639134. A pipeline started on a ref runs **every** job
that matches; those without `tags: [local]` use paid minutes, so look at the
CI file first and cancel what you did not mean to start.

Because the runner is protected, a patch on an unprotected branch is **not**
picked up. To test a patch in CI either (a) ask the owner to unprotect the
runner (Group → Build → Runners → Edit → untick "Protected"), or (b) test
the patch locally.

## Quick loop (no CI, no cost)

- App: `./gradlew --offline -q :core:domain:test :core:data:testDebugUnitTest :app:compileDebugKotlin`
- Server: `ATWEB_VAR=<dir> <venv>/bin/python manage.py test` (Django 4.2 venv; see the
  scratchpad of the session that built it, or create one: `python3 -m venv`,
  `pip install django<5 ...` as in `server/requirements*`).
- Python repos: `python3 -m unittest` in the repository.
- Containers by hand: `XDG_RUNTIME_DIR=/tmp/user/1000 podman run --rm --pid host -v "$PWD":/w -w /w debian:trixie-slim ...`

## Known limits and things to verify

- Verified 2026-11-07: job `local-linux` of python3-activitytrack (107 unit tests) ran to
  success on this runner. Not verified: `services:`, Android SDK images, jobs
  that need much RAM/disk.
- `/tmp/user/1000` is cleared at reboot: restart `ci-runner` afterwards.
