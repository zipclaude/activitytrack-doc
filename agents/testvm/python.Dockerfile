# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Flavio Visentin <flavio-activitytrack@infraconsulting.it>
# Python test image of the test VM runner (tag testvm): the Debian trixie packages the
# unit tests of the six repositories need, so that the jobs do not run apt-get each time.
# Built by hand on the VM, not in CI:
#   mkdir /tmp/b && cp python.Dockerfile /tmp/b/Dockerfile && docker build -t activitytrack/pytest:trixie /tmp/b
FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
 && apt-get install -y -qq --no-install-recommends git ca-certificates python3 \
      python3-cryptography python3-keyring python3-django python3-segno python3-argon2 \
      python3-psycopg python3-pyqt6 libegl1 dbus flake8 gettext > /dev/null \
 && rm -rf /var/lib/apt/lists/*
