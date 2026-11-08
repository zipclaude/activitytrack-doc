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
- `manual/` (to come): user and administrator manuals, installation guides, brochure.
  They move here from the code repositories and are packaged as `activitytrack-doc`.

What stays with the code, because it changes together with it: SPEC, SYNC, POLICY,
PLUGINS, INTERCHANGE, DESIGN and ARCHITECTURE.

This repository follows the same branches and version numbers as the others
(see the workflow). No secrets, tokens or personal data here: it is public.
