# Using the owner's local GitLab runner (for a remote agent)

You work on the ActivityTrack repositories (`gitlab.com/activitytrack/*`) from
another machine. You cannot reach the owner's computer: everything goes through
GitLab. This note is self-contained.

## Rules

1. **No pipeline starts on its own** any more. The `.gitlab-ci.yml` of the six
   repositories accept only pipelines started by hand ("Run pipeline") or
   through the pipelines API. Pushes, merge requests and tags start nothing.
   (This is true once the owner has merged the `ci-manual-start` MRs.)
2. **Start a pipeline only when the owner tells you to.** The shared runners of
   gitlab.com are paid for: any job without the tag `local` spends credits.
   Before starting one, read `.gitlab-ci.yml` and know which jobs it will run.
3. Test your patches in your own environment first (unit tests per repository:
   Gradle for the app, `manage.py test` for the server, `unittest` for the
   Python repositories). Use CI only to confirm, before a release.
4. Never put tokens, keys or passwords in a file, commit, MR text or job log.
   The repositories and their MRs are public.

## What the local runner is

A GitLab runner on the owner's machine, registered for the whole group:

- name `zipclaude`, id 58715863, tag `local`
- runs **only jobs that declare `tags: [local]`** (untagged jobs do not use it)
- **protected**: it takes jobs of protected refs only (`main` and tags `v*`),
  so a pipeline on your feature branch will wait forever with "stuck, no
  runner"; ask the owner to untick *Protected* (Group → Build → Runners → edit)
  while you test, and to tick it again afterwards
- rootless podman, Linux containers only; no Windows jobs, no Docker-in-Docker,
  no privileged mode, one job at a time, `pid_mode = host`
- **it is not always on**: the owner starts it on request. If it is offline a
  job with the tag stays `pending`.

Check it from GitLab (needs a token that can read the group's runners):

```
curl -s -H "PRIVATE-TOKEN: $TOKEN" https://gitlab.com/api/v4/runners/58715863 \
  | jq '{status,online,tag_list,access_level}'
```

## Making a job use it

```yaml
my-job:
  tags: [local]
  image: debian:trixie-slim     # any public image; the default is debian:trixie-slim
  script:
    - ...
```

Keep the job also valid on the SaaS runners if it is meant to stay in the
repository after the test (remove the tag, or the owner decides which jobs move).

## Starting and following a pipeline (only on the owner's word)

```
# project ids: app 88636043, web 88639123, lib 88639115,
#              cli 88639128, tui 88639133, desktop 88639134
curl -s -X POST -H "PRIVATE-TOKEN: $TOKEN" \
  "https://gitlab.com/api/v4/projects/<id>/pipeline?ref=<branch-or-tag>"
curl -s -H "PRIVATE-TOKEN: $TOKEN" \
  "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>/jobs" | jq '.[]|{name,status,tag_list}'
curl -s -X POST -H "PRIVATE-TOKEN: $TOKEN" \
  "https://gitlab.com/api/v4/projects/<id>/pipelines/<pid>/cancel"
```

If a job without `local` starts by mistake, **cancel the pipeline at once**.

## Reporting

The runner has run one real job to success (python3-activitytrack unit tests,
107 tests). Not verified yet: `services:`, large images, long jobs. If a job fails
in the preparation, report the first error lines of the job log and the pipeline
URL to the owner; do not "fix" it with `privileged: true`, `docker:dind` or by
switching to the shared runners.
