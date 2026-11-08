# ActivityTrack: documentation

The one place for the documentation of the ActivityTrack projects, for users and
for the people (and agents) who work on them.

| Project | What it is |
|---|---|
| [activitytrack](https://gitlab.com/activitytrack/activitytrack) | Android app |
| [activitytrack-web](https://gitlab.com/activitytrack/activitytrack-web) | Server (Django) |
| [python3-activitytrack](https://gitlab.com/activitytrack/python3-activitytrack) | Library for the PC |
| [activitytrack-cli](https://gitlab.com/activitytrack/activitytrack-cli), [-tui](https://gitlab.com/activitytrack/activitytrack-tui), [-desktop](https://gitlab.com/activitytrack/activitytrack-desktop) | Command line, text interface, tray application |

## Contents

- `agents/`: how we work. Start with [`agents/workflow.md`](agents/workflow.md) (branches,
  versions, releases, security patches), then [`agents/local-ci.md`](agents/local-ci.md)
  (the local runner) and [`agents/local-ci-remote-agent.md`](agents/local-ci-remote-agent.md)
  (the same, for an agent that works from another machine).
- `manual/app`, `manual/server`, `manual/desktop`: the manuals (Italian and English); `brochure/`: the brochure.
  They come from the code repositories, with their history, and are packaged as `activitytrack-doc`.

What stays with the code, because it changes together with it: SPEC, SYNC, POLICY,
PLUGINS, INTERCHANGE, DESIGN and ARCHITECTURE.

This repository follows the same branches and version numbers as the others
(see the workflow). No secrets, tokens or personal data here: it is public.

## Build

`scripts/build-manual.sh` makes the PDFs (pandoc, graphviz, Chromium) into `build/manual`; the CI job
`manual` does it on a merge request into `next`, and on a tag it publishes the PDFs and the Debian
package `activitytrack-doc` (`/usr/share/doc/activitytrack-doc/{it,en}`). See `CLAUDE.md`.
