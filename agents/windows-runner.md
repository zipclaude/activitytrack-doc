# A Windows 11 runner for the full pipeline (to set up when there is time)

The paid shared Windows runners of GitLab run the jobs `windows`, `windows-exe` and
`windows-installer` of cli, tui and desktop: the only jobs that start the packaged executables.
They run for **stable tags** only. A local Windows 11 machine does the same for free, and checks a
real client system (the shared runners are Windows Server). This is the plan; nothing of it is
installed yet.

## Choice of system

**Windows 11 Pro** (recommended). The users' system; complements the shared runners (Server).
Server 2025 Core has no desktop components that Qt and the installer need; use it only for a
runner that runs the unit tests of the CLI. The 90-day Windows 11 Enterprise evaluation image works
to try the setup; for lasting use a Pro licence is needed.

## The virtual machine

It cannot live in the LXC container that hosts the Linux runner (no KVM there): on the libvirt
host, or on another machine.

- UEFI (OVMF) and a virtual TPM 2.0 (`swtpm`): Windows 11 asks for both. Without them the
  installer can be told to skip the checks (registry `LabConfig`, unsupported but common).
- 4 vCPU, 8 GB RAM, 80 GB disk (qcow2), virtio disk and network (the drivers ISO `virtio-win`).
- A local user for the runner, no Microsoft account, automatic login or a service account.
- Windows Update on, but outside a build; Defender on (the executables are not signed: this is
  how a user sees them).
- Take a snapshot ("clean") once it is set up; revert to it before each release run, so every run
  starts from the same system.

## What the jobs need in the machine

They are written for the shared runner's image: PowerShell 5.1 and Chocolatey.

1. Chocolatey (https://chocolatey.org/install), then in an administrator PowerShell:
   `choco install git -y`. The jobs install Python 3.13 and Inno Setup themselves
   (`choco install python313`, `choco install innosetup`).
2. The runner (an administrator PowerShell):
   ```
   mkdir C:\GitLab-Runner ; cd C:\GitLab-Runner
   Invoke-WebRequest -Uri https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-windows-amd64.exe -OutFile gitlab-runner.exe
   .\gitlab-runner.exe register --url https://gitlab.com --token <the runner token> --executor shell
   ```
   In `config.toml` set `shell = "powershell"` (5.1: the jobs rely on its behaviour).
3. The runner token: *Group activitytrack → Build → Runners → New group runner*, tag
   `windows-local`, **Protected on** (stable tags only), *Run untagged jobs* off. Paste it into the
   command above on the machine; do not write it in a file of a repository.

## Using it from the pipelines

The Windows jobs name the tag `saas-windows-medium-amd64`. Registering the VM with that same tag
would put both runners in one pool: GitLab may choose the paid one. So give the VM its own tag
(`windows-local`) and make the jobs' tag a variable (to verify on the first try, GitLab documents
variables in `tags`):

```yaml
variables:
  WINDOWS_TAG: saas-windows-medium-amd64     # the paid shared runner; "windows-local" for the VM
windows:
  tags: [$WINDOWS_TAG]
```

A stable release then starts with `WINDOWS_TAG=windows-local` (Run pipeline → variables, or
`variables[WINDOWS_TAG]=windows-local` in the API call). The shared runner stays the default.

## Routine

1. Revert the snapshot "clean", start the VM, check the runner in *Build → Runners* (online).
2. Start the pipeline on the stable tag with `WINDOWS_TAG=windows-local`.
3. When the jobs end, shut the VM down. A failure shows what the real system does that Wine
   cannot show: the first thing to look at is Defender and SmartScreen, the console code page
   (`[Console]::OutputEncoding`) and the user profile paths.

## Not decided yet

- Whether the VM is started by hand or by a libvirt hook when a job is waiting.
- Whether to sign the executables (a certificate costs money; today they are not signed and the
  release notes say so).
